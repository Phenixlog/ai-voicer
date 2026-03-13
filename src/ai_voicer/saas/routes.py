"""SaaS API routes - extends the base API with auth, billing, usage."""
from fastapi import APIRouter, HTTPException, Request, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import time
import threading

from .database import get_db
from .models import User, UserSettings, Plan, Subscription
from .auth import (
    create_access_token, create_refresh_token, verify_refresh_token,
    revoke_refresh_token, revoke_all_user_tokens, get_current_user
)
from .billing import (
    init_plans, get_plan_by_code, create_checkout_session,
    create_portal_session, handle_webhook_event
)
from .usage import check_quota, record_usage, get_usage_stats

# Import existing service for transcription
from ..config import AppConfig, load_config
from ..mistral_service import MistralTranscriptionService

router = APIRouter(prefix="/v1")

_mistral_service_lock = threading.Lock()
_mistral_service: Optional[MistralTranscriptionService] = None
_mistral_service_signature: Optional[tuple] = None

# Request/Response schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: Optional[str] = None  # For magic link, password optional

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes

class RefreshRequest(BaseModel):
    refresh_token: str

class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    google_token: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    locale: str
    plan: str
    created_at: str

class SettingsUpdate(BaseModel):
    hotkey: Optional[str] = None
    trigger_mode: Optional[str] = None
    language: Optional[str] = None
    style_mode: Optional[str] = None
    hud_enabled: Optional[bool] = None

class TranscriptionResponse(BaseModel):
    transcript: str
    text: str
    request_id: str
    latency_ms: int
    transcribe_ms: Optional[int] = None
    structure_ms: Optional[int] = None


def _config_signature(config: AppConfig) -> tuple:
    return (
        config.mistral_api_key or "",
        config.transcribe_model,
        config.structure_model,
        config.language or "",
        config.context_bias or "",
        bool(config.enable_structuring),
    )


def _get_mistral_service() -> tuple[MistralTranscriptionService, AppConfig]:
    global _mistral_service, _mistral_service_signature

    config = load_config()
    signature = _config_signature(config)

    with _mistral_service_lock:
        if _mistral_service is None or _mistral_service_signature != signature:
            _mistral_service = MistralTranscriptionService(config)
            _mistral_service_signature = signature

        # _mistral_service is guaranteed to be set inside the lock above.
        return _mistral_service, config


# Auth routes
@router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login with email (magic link or password)."""
    db = get_db()
    try:
        # For now, simple implementation - create user if not exists
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            # Auto-create user (simplified onboarding)
            user = User(
                id=str(uuid.uuid4()),
                email=request.email,
                name=request.email.split("@")[0],
                status="active"
            )
            db.add(user)
            
            # Create default settings
            settings = UserSettings(user_id=user.id)
            db.add(settings)
            
            # Create free subscription
            free_plan = get_plan_by_code("free")
            subscription = Subscription(
                id=str(uuid.uuid4()),
                user_id=user.id,
                plan_id=free_plan.id if free_plan else None,
                status="active"
            )
            db.add(subscription)
            db.commit()
        
        if user.status != "active":
            raise HTTPException(status_code=403, detail="Account suspended")
        
        # Generate tokens
        access_token = create_access_token(user.id)
        _, refresh_token = create_refresh_token(user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    finally:
        db.close()


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    """Refresh access token."""
    user_id = verify_refresh_token(request.refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    access_token = create_access_token(user_id)
    _, new_refresh_token = create_refresh_token(user_id)
    
    # Revoke old refresh token
    revoke_refresh_token(request.refresh_token)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.post("/auth/logout")
async def logout(request: RefreshRequest, current_user: User = Depends(get_current_user)):
    """Logout - revoke refresh token."""
    revoke_refresh_token(request.refresh_token)
    return {"message": "Logged out successfully"}


@router.post("/auth/logout-all")
async def logout_all(current_user: User = Depends(get_current_user)):
    """Logout from all devices."""
    count = revoke_all_user_tokens(current_user.id)
    return {"message": f"Revoked {count} sessions"}


# User routes
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    db = get_db()
    try:
        subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
        plan_code = "free"
        if subscription:
            plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
            if plan:
                plan_code = plan.code
        
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            locale=current_user.locale,
            plan=plan_code,
            created_at=current_user.created_at.isoformat()
        )
    finally:
        db.close()


@router.get("/me/settings")
async def get_settings(current_user: User = Depends(get_current_user)):
    """Get user settings."""
    db = get_db()
    try:
        settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not settings:
            settings = UserSettings(user_id=current_user.id)
            db.add(settings)
            db.commit()
        
        return {
            "hotkey": settings.hotkey,
            "trigger_mode": settings.trigger_mode,
            "language": settings.language,
            "style_mode": settings.style_mode,
            "context_bias": settings.context_bias,
            "hud_enabled": settings.hud_enabled,
        }
    finally:
        db.close()


@router.patch("/me/settings")
async def update_settings(
    update: SettingsUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user settings."""
    db = get_db()
    try:
        settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if not settings:
            settings = UserSettings(user_id=current_user.id)
            db.add(settings)
        
        if update.hotkey is not None:
            settings.hotkey = update.hotkey
        if update.trigger_mode is not None:
            settings.trigger_mode = update.trigger_mode
        if update.language is not None:
            settings.language = update.language
        if update.style_mode is not None:
            settings.style_mode = update.style_mode
        if update.hud_enabled is not None:
            settings.hud_enabled = update.hud_enabled
        
        db.commit()
        return {"message": "Settings updated"}
    finally:
        db.close()


# Usage routes
@router.get("/usage/current-period")
async def get_current_usage(current_user: User = Depends(get_current_user)):
    """Get usage for current billing period."""
    return get_usage_stats(current_user.id)


# Billing routes
@router.get("/plans")
async def list_plans():
    """List available plans."""
    db = get_db()
    try:
        plans = db.query(Plan).filter(Plan.active == True).all()
        return {
            "plans": [
                {
                    "id": p.id,
                    "code": p.code,
                    "name": p.name,
                    "monthly_minutes": p.monthly_minutes,
                    "price_cents": p.price_cents,
                    "currency": p.currency,
                }
                for p in plans
            ]
        }
    finally:
        db.close()


@router.post("/billing/checkout-session")
async def create_checkout(
    plan_code: str,
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """Create Stripe checkout session."""
    base_url = str(request.base_url).rstrip("/")
    
    try:
        session = create_checkout_session(
            current_user,
            plan_code,
            success_url=f"{base_url}/billing/success",
            cancel_url=f"{base_url}/billing/cancel"
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/billing/portal-session")
async def create_portal(
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """Create Stripe customer portal session."""
    base_url = str(request.base_url).rstrip("/")
    
    try:
        session = create_portal_session(current_user, return_url=f"{base_url}/settings/billing")
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks."""
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")
    
    success = handle_webhook_event(payload, signature)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid webhook")
    
    return {"status": "ok"}


# Transcription route with auth and metering
@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_saas(
    audio: UploadFile = File(...),
    structured: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transcribe audio with user auth and quota checking."""
    import os
    import tempfile

    start_time = time.perf_counter()
    
    # Save uploaded file temporarily
    suffix = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
    with tempfile.NamedTemporaryFile(prefix="theoria-", suffix=suffix, delete=False) as tmp:
        data = await audio.read()
        tmp.write(data)
        audio_path = tmp.name
        audio_size = len(data)
    
    # Estimate audio duration (approximate from file size)
    # WAV: 16-bit, 16kHz, mono = 32KB per second
    estimated_seconds = audio_size / 32000 if suffix == ".wav" else audio_size / 16000
    
    try:
        # Check quota
        allowed, reason = check_quota(current_user.id, estimated_seconds)
        if not allowed:
            record_usage(
                user_id=current_user.id,
                audio_seconds=0,
                provider="mistral",
                model=None,
                success=False,
                error_code="quota_exceeded"
            )
            raise HTTPException(
                status_code=402,
                detail=f"Quota exceeded. Upgrade your plan at /billing/checkout-session"
            )
        
        # Reuse a shared Mistral service instance across requests.
        service, config = _get_mistral_service()

        transcribe_started = time.perf_counter()
        transcript = service.transcribe_file(audio_path)
        transcribe_ms = int((time.perf_counter() - transcribe_started) * 1000)

        structure_ms = None
        if structured:
            structure_started = time.perf_counter()
            final_text = service.structure_text(transcript)
            structure_ms = int((time.perf_counter() - structure_started) * 1000)
        else:
            final_text = transcript

        latency_ms = int((time.perf_counter() - start_time) * 1000)
        
        # Record successful usage
        request_id = record_usage(
            user_id=current_user.id,
            audio_seconds=estimated_seconds,
            provider="mistral",
            model=config.transcribe_model,
            success=True,
            latency_ms=latency_ms,
            cost_estimate_cents=int(estimated_seconds * 0.1)  # Approx 0.1c per second
        )
        
        return TranscriptionResponse(
            transcript=transcript,
            text=final_text,
            request_id=request_id,
            latency_ms=latency_ms,
            transcribe_ms=transcribe_ms,
            structure_ms=structure_ms,
        )
        
    except HTTPException:
        raise
    except Exception as exc:
        # Record failed usage
        record_usage(
            user_id=current_user.id,
            audio_seconds=estimated_seconds,
            provider="mistral",
            model=None,
            success=False,
            error_code="transcription_failed"
        )
        raise HTTPException(
            status_code=502,
            detail=f"Transcription error: {exc.__class__.__name__}"
        )
    finally:
        try:
            os.remove(audio_path)
        except OSError:
            pass
