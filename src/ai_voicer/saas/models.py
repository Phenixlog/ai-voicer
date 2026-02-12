"""Database models for Théoria SaaS."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Float, Text, Index
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    locale = Column(String(10), default="fr")
    status = Column(String(20), default="active")  # active, suspended, deleted
    
    # OAuth provider info
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    
    # Relationships
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    usage_events = relationship("UsageEvent", back_populates="user")


class UserSettings(Base):
    __tablename__ = "user_settings"
    
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    hotkey = Column(String(50), default="f8")
    trigger_mode = Column(String(20), default="hold")  # hold, toggle
    language = Column(String(10), default="fr")
    style_mode = Column(String(50), default="message")  # message, email, note, prompt
    context_bias = Column(Text, nullable=True)
    hud_enabled = Column(Boolean, default=True)
    duck_output_audio = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="settings")


class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(String(36), primary_key=True)
    code = Column(String(20), unique=True, nullable=False, index=True)  # free, pro, power
    name = Column(String(100), nullable=False)
    monthly_minutes = Column(Integer, nullable=False)  # 0 = unlimited
    price_cents = Column(Integer, nullable=False)  # 0 = free
    currency = Column(String(3), default="eur")
    stripe_price_id = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)
    
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    plan_id = Column(String(36), ForeignKey("plans.id"), nullable=False)
    
    # Stripe integration
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True, unique=True, index=True)
    stripe_price_id = Column(String(255), nullable=True)
    
    status = Column(String(20), default="incomplete")  # incomplete, active, canceled, past_due
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")
    
    __table_args__ = (
        Index('idx_subscription_user_status', 'user_id', 'status'),
    )


class UsageEvent(Base):
    __tablename__ = "usage_events"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    request_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Usage data
    audio_seconds = Column(Float, nullable=False)
    provider = Column(String(50), default="mistral")
    model = Column(String(100), nullable=True)
    
    # Status
    success = Column(Boolean, default=True)
    error_code = Column(String(50), nullable=True)
    
    # Performance & cost tracking
    latency_ms = Column(Integer, nullable=True)
    cost_estimate_cents = Column(Integer, nullable=True)  # Cost in 1/100 of cent
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    user = relationship("User", back_populates="usage_events")
    
    __table_args__ = (
        Index('idx_usage_user_created', 'user_id', 'created_at'),
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    device_info = Column(String(255), nullable=True)
