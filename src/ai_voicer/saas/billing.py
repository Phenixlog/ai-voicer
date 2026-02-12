"""Stripe billing integration for Théoria SaaS."""
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

import stripe
from sqlalchemy.orm import Session

from .database import get_db_context as get_db
from .models import User, Plan, Subscription

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Default plans configuration
DEFAULT_PLANS = [
    {
        "id": str(uuid.uuid4()),
        "code": "free",
        "name": "Free",
        "monthly_minutes": 30,
        "price_cents": 0,
        "stripe_price_id": None,
    },
    {
        "id": str(uuid.uuid4()),
        "code": "pro",
        "name": "Pro",
        "monthly_minutes": 300,  # 5 hours
        "price_cents": 1200,  # €12
        "stripe_price_id": os.getenv("STRIPE_PRICE_PRO", ""),
    },
    {
        "id": str(uuid.uuid4()),
        "code": "power",
        "name": "Power",
        "monthly_minutes": 0,  # unlimited
        "price_cents": 2900,  # €29
        "stripe_price_id": os.getenv("STRIPE_PRICE_POWER", ""),
    },
]


def init_plans():
    """Initialize default plans in database."""
    with get_db() as db:
        for plan_data in DEFAULT_PLANS:
            existing = db.query(Plan).filter(Plan.code == plan_data["code"]).first()
            if not existing:
                plan = Plan(**plan_data)
                db.add(plan)
        db.commit()


def get_plan_by_code(code: str) -> Optional[Plan]:
    """Get plan by code (free, pro, power)."""
    with get_db() as db:
        return db.query(Plan).filter(Plan.code == code, Plan.active == True).first()


def get_or_create_stripe_customer(user: User) -> str:
    """Get or create Stripe customer for user."""
    # Check existing subscription
    with get_db() as db:
        subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        
        if subscription and subscription.stripe_customer_id:
            return subscription.stripe_customer_id
        
        # Create new Stripe customer
        customer = stripe.Customer.create(
            email=user.email,
            name=user.name,
            metadata={"user_id": user.id}
        )
        
        if not subscription:
            # Create free subscription
            free_plan = get_plan_by_code("free")
            subscription = Subscription(
                id=str(uuid.uuid4()),
                user_id=user.id,
                plan_id=free_plan.id,
                stripe_customer_id=customer.id,
                status="active",
            )
            db.add(subscription)
        else:
            subscription.stripe_customer_id = customer.id
        
        db.commit()
        return customer.id


def create_checkout_session(user: User, plan_code: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
    """Create Stripe checkout session for plan upgrade."""
    plan = get_plan_by_code(plan_code)
    if not plan or plan.code == "free":
        raise ValueError("Invalid plan")
    
    if not plan.stripe_price_id:
        raise ValueError("Plan not configured for Stripe")
    
    customer_id = get_or_create_stripe_customer(user)
    
    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{
            "price": plan.stripe_price_id,
            "quantity": 1,
        }],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"user_id": user.id, "plan_code": plan_code},
    )
    
    return {"session_id": session.id, "url": session.url}


def create_portal_session(user: User, return_url: str) -> Dict[str, Any]:
    """Create Stripe customer portal session."""
    with get_db() as db:
        subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        
        if not subscription or not subscription.stripe_customer_id:
            raise ValueError("No Stripe customer found")
        
        session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url=return_url,
        )
        
        return {"url": session.url}


def handle_webhook_event(payload: bytes, signature: str) -> bool:
    """Handle Stripe webhook event."""
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return False
    
    with get_db() as db:
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            _handle_checkout_completed(db, session)
        
        elif event["type"] == "customer.subscription.updated":
            subscription = event["data"]["object"]
            _handle_subscription_updated(db, subscription)
        
        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            _handle_subscription_deleted(db, subscription)
        
        db.commit()
    
    return True


def _handle_checkout_completed(db: Session, session: Dict):
    """Process completed checkout."""
    user_id = session.get("metadata", {}).get("user_id")
    plan_code = session.get("metadata", {}).get("plan_code")
    
    if not user_id or not plan_code:
        return
    
    plan = get_plan_by_code(plan_code)
    if not plan:
        return
    
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    
    if subscription:
        subscription.plan_id = plan.id
        subscription.stripe_subscription_id = session.get("subscription")
        subscription.status = "active"
        subscription.current_period_start = datetime.fromtimestamp(
            session.get("subscription_details", {}).get("current_period_start", 0)
        )
        subscription.current_period_end = datetime.fromtimestamp(
            session.get("subscription_details", {}).get("current_period_end", 0)
        )


def _handle_subscription_updated(db: Session, stripe_sub: Dict):
    """Process subscription update."""
    stripe_customer_id = stripe_sub.get("customer")
    
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_sub["id"]
    ).first()
    
    if not subscription:
        # Try finding by customer
        subscription = db.query(Subscription).filter(
            Subscription.stripe_customer_id == stripe_customer_id
        ).first()
    
    if subscription:
        subscription.status = stripe_sub["status"]
        subscription.current_period_start = datetime.fromtimestamp(stripe_sub["current_period_start"])
        subscription.current_period_end = datetime.fromtimestamp(stripe_sub["current_period_end"])


def _handle_subscription_deleted(db: Session, stripe_sub: Dict):
    """Process subscription cancellation - downgrade to free."""
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_sub["id"]
    ).first()
    
    if subscription:
        free_plan = get_plan_by_code("free")
        subscription.plan_id = free_plan.id
        subscription.status = "canceled"
        subscription.canceled_at = datetime.utcnow()
        subscription.stripe_subscription_id = None
