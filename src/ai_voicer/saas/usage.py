"""Usage metering and quota management for Théoria SaaS."""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import get_db_context as get_db
from .models import User, Plan, Subscription, UsageEvent


def get_user_plan_and_minutes(user_id: str) -> Tuple[Optional[Plan], int, int]:
    """Get user's plan and usage info. Returns (plan, monthly_minutes, used_minutes)."""
    with get_db() as db:
        # Get user's subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
        
        if not subscription:
            # No subscription = free plan
            plan = db.query(Plan).filter(Plan.code == "free").first()
            monthly_minutes = plan.monthly_minutes if plan else 30
        else:
            plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
            monthly_minutes = plan.monthly_minutes if plan else 30
        
        # Calculate used minutes in current period
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        used_seconds = db.query(func.sum(UsageEvent.audio_seconds)).filter(
            UsageEvent.user_id == user_id,
            UsageEvent.success == True,
            UsageEvent.created_at >= period_start
        ).scalar() or 0
        
        used_minutes = int(used_seconds / 60)
        
        return plan, monthly_minutes, used_minutes


def check_quota(user_id: str, audio_seconds: float) -> Tuple[bool, str]:
    """Check if user has enough quota for the request."""
    plan, monthly_minutes, used_minutes = get_user_plan_and_minutes(user_id)
    
    if monthly_minutes == 0:  # Unlimited
        return True, "ok"
    
    requested_minutes = audio_seconds / 60
    remaining = monthly_minutes - used_minutes
    
    if remaining <= 0:
        return False, "quota_exceeded"
    
    if requested_minutes > remaining:
        return False, "partial_quota"
    
    return True, "ok"


def record_usage(
    user_id: str,
    audio_seconds: float,
    provider: str,
    model: Optional[str],
    success: bool,
    latency_ms: Optional[int] = None,
    cost_estimate_cents: Optional[int] = None,
    error_code: Optional[str] = None
) -> str:
    """Record a usage event. Returns request_id."""
    request_id = f"req_{uuid.uuid4().hex[:24]}"
    
    with get_db() as db:
        event = UsageEvent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            request_id=request_id,
            audio_seconds=audio_seconds,
            provider=provider,
            model=model,
            success=success,
            latency_ms=latency_ms,
            cost_estimate_cents=cost_estimate_cents,
            error_code=error_code,
        )
        db.add(event)
        db.commit()
    
    return request_id


def get_usage_stats(user_id: str) -> dict:
    """Get usage statistics for user."""
    with get_db() as db:
        # Current period
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Total usage this period
        period_stats = db.query(
            func.count(UsageEvent.id).label("count"),
            func.sum(UsageEvent.audio_seconds).label("total_seconds"),
            func.avg(UsageEvent.latency_ms).label("avg_latency"),
        ).filter(
            UsageEvent.user_id == user_id,
            UsageEvent.success == True,
            UsageEvent.created_at >= period_start
        ).first()
        
        # Success rate
        total_requests = db.query(func.count(UsageEvent.id)).filter(
            UsageEvent.user_id == user_id,
            UsageEvent.created_at >= period_start
        ).scalar() or 0
        
        successful_requests = db.query(func.count(UsageEvent.id)).filter(
            UsageEvent.user_id == user_id,
            UsageEvent.success == True,
            UsageEvent.created_at >= period_start
        ).scalar() or 0
        
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 100
        
        # Plan info
        plan, monthly_minutes, used_minutes = get_user_plan_and_minutes(user_id)
        
        return {
            "period_start": period_start.isoformat(),
            "period_end": (period_start + timedelta(days=32)).replace(day=1).isoformat(),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate_percent": round(success_rate, 1),
            "total_audio_seconds": round(period_stats.total_seconds or 0, 1),
            "total_audio_minutes": round((period_stats.total_seconds or 0) / 60, 1),
            "average_latency_ms": round(period_stats.avg_latency or 0, 0),
            "plan": {
                "code": plan.code if plan else "free",
                "name": plan.name if plan else "Free",
                "monthly_minutes": monthly_minutes,
            },
            "usage": {
                "used_minutes": used_minutes,
                "remaining_minutes": (monthly_minutes - used_minutes) if monthly_minutes > 0 else None,
                "percent_used": (used_minutes / monthly_minutes * 100) if monthly_minutes > 0 else 0,
            }
        }
