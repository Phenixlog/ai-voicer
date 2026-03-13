"""SaaS client for Théoria desktop - handles auth and API calls."""
import os
import json
import time
import httpx
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class SaasCredentials:
    """Stored SaaS credentials."""
    user_id: Optional[str] = None
    email: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[float] = None
    
    def is_expired(self) -> bool:
        if not self.expires_at:
            return True
        # Consider expired 60s before actual expiry
        return time.time() > (self.expires_at - 60)
    
    def is_logged_in(self) -> bool:
        return bool(self.access_token and not self.is_expired())


class SaasAuthManager:
    """Manages SaaS authentication for desktop client."""
    
    def __init__(self, backend_url: str, config_dir: Optional[Path] = None):
        self.backend_url = backend_url.rstrip("/")
        self.config_dir = config_dir or Path.home() / "Library" / "Application Support" / "Theoria"
        self.credentials_file = self.config_dir / "saas_credentials.json"
        self._credentials: Optional[SaasCredentials] = None
        self._http = httpx.Client(
            timeout=httpx.Timeout(30.0, connect=10.0, read=30.0),
            limits=httpx.Limits(max_keepalive_connections=8, max_connections=16),
        )
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_credentials(self) -> SaasCredentials:
        """Load credentials from file."""
        # Always reload from disk so separate processes (desktop UI/daemon/autostart)
        # see fresh credentials immediately after login/logout.
        if self.credentials_file.exists():
            try:
                data = json.loads(self.credentials_file.read_text())
                self._credentials = SaasCredentials(**data)
                return self._credentials
            except (json.JSONDecodeError, TypeError):
                pass
        
        self._credentials = SaasCredentials()
        return self._credentials
    
    def _save_credentials(self, creds: SaasCredentials):
        """Save credentials to file with restricted permissions."""
        self._credentials = creds
        self.credentials_file.write_text(json.dumps(asdict(creds), indent=2))
        # Restrict permissions (user only)
        os.chmod(self.credentials_file, 0o600)
    
    def is_logged_in(self) -> bool:
        """Check if user has (or can recover) a valid access token."""
        return bool(self.get_access_token())
    
    def get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """Get valid access token, refreshing/recovering session when possible."""
        creds = self._load_credentials()

        if creds.access_token and not creds.is_expired() and not force_refresh:
            return creds.access_token

        if creds.refresh_token and self._refresh_token(creds):
            refreshed = self._load_credentials()
            if refreshed.access_token:
                return refreshed.access_token

        # Local/dev convenience fallback:
        # if refresh token is invalid but email is known, perform a silent re-login.
        if creds.email and self.login(creds.email):
            relogged = self._load_credentials()
            return relogged.access_token

        return None
    
    def _refresh_token(self, creds: SaasCredentials) -> bool:
        """Refresh access token using refresh token."""
        if not creds.refresh_token:
            return False
        
        try:
            response = self._http.post(
                f"{self.backend_url}/v1/auth/refresh",
                json={"refresh_token": creds.refresh_token},
            )
            
            if response.status_code == 200:
                data = response.json()
                new_creds = SaasCredentials(
                    user_id=creds.user_id,
                    email=creds.email,
                    access_token=data["access_token"],
                    refresh_token=data["refresh_token"],
                    expires_at=time.time() + data.get("expires_in", 900)
                )
                self._save_credentials(new_creds)
                return True
            else:
                # Refresh failed, clear credentials
                self.logout()
                return False
                
        except httpx.RequestError:
            return False
    
    def login(self, email: str, password: Optional[str] = None) -> bool:
        """Login with email (magic link or password)."""
        try:
            response = self._http.post(
                f"{self.backend_url}/v1/auth/login",
                json={"email": email, "password": password},
            )
            
            if response.status_code == 200:
                data = response.json()
                creds = SaasCredentials(
                    email=email,
                    access_token=data["access_token"],
                    refresh_token=data["refresh_token"],
                    expires_at=time.time() + data.get("expires_in", 900)
                )
                self._save_credentials(creds)
                return True
            
            return False
            
        except httpx.RequestError as e:
            print(f"Login failed: {e}")
            return False
    
    def logout(self):
        """Logout and clear credentials."""
        creds = self._load_credentials()
        
        # Try to revoke on server
        if creds.refresh_token:
            try:
                self._http.post(
                    f"{self.backend_url}/v1/auth/logout",
                    headers=self.get_auth_headers(),
                    json={"refresh_token": creds.refresh_token},
                )
            except httpx.RequestError:
                pass
        
        # Clear local credentials
        if self.credentials_file.exists():
            self.credentials_file.unlink()
        self._credentials = SaasCredentials()
    
    def get_auth_headers(self) -> dict:
        """Get authorization headers for API requests."""
        token = self.get_access_token()
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def close(self) -> None:
        self._http.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


class SaasTranscriptionService:
    """Transcription service that uses SaaS API with auth."""
    
    def __init__(self, backend_url: str, auth_manager: Optional[SaasAuthManager] = None):
        self.backend_url = backend_url.rstrip("/")
        self.auth = auth_manager or SaasAuthManager(backend_url)
        self._http = httpx.Client(
            timeout=httpx.Timeout(120.0, connect=10.0, read=120.0),
            limits=httpx.Limits(max_keepalive_connections=8, max_connections=16),
        )
        self.last_latency_ms: Optional[int] = None
        self.last_transcribe_ms: Optional[int] = None
        self.last_structure_ms: Optional[int] = None
    
    def transcribe_and_structure_file(self, audio_path: str) -> Tuple[str, str]:
        """Transcribe audio file using SaaS API."""
        token = self.auth.get_access_token()
        if not token:
            raise RuntimeError(
                "Not logged in. Run: python run_saas_daemon.py login <email>"
            )
        self.last_latency_ms = None
        self.last_transcribe_ms = None
        self.last_structure_ms = None

        headers = {"Authorization": f"Bearer {token}"}
        with open(audio_path, "rb") as file_obj:
            audio_bytes = file_obj.read()

        def _post_with_headers(request_headers: dict) -> httpx.Response:
            files = {
                "audio": (os.path.basename(audio_path), audio_bytes, "audio/wav")
            }
            return self._http.post(
                f"{self.backend_url}/v1/transcribe",
                headers=request_headers,
                files=files,
                params={"structured": "true"},
            )

        response = _post_with_headers(headers)

        if response.status_code == 401:
            # Token can be invalid after backend restart (e.g. changed JWT secret).
            # Force-refresh (or silent re-login) once, then retry.
            recovered = self.auth.get_access_token(force_refresh=True)
            if recovered:
                response = _post_with_headers({"Authorization": f"Bearer {recovered}"})

        if response.status_code == 401:
            raise RuntimeError("Authentication expired. Please login again.")
        
        if response.status_code == 402:
            data = response.json()
            raise RuntimeError(f"Quota exceeded: {data.get('detail', 'Upgrade your plan')}")
        
        if response.status_code >= 400:
            detail = response.text.strip()
            raise RuntimeError(f"Transcription failed ({response.status_code}): {detail}")
        
        payload = response.json()
        transcript = payload.get("transcript", "") or ""
        text = payload.get("text", "") or transcript
        self.last_latency_ms = payload.get("latency_ms")
        self.last_transcribe_ms = payload.get("transcribe_ms")
        self.last_structure_ms = payload.get("structure_ms")

        return transcript, text
    
    def get_usage(self) -> dict:
        """Get current usage stats."""
        headers = self.auth.get_auth_headers()

        response = self._http.get(
            f"{self.backend_url}/v1/usage/current-period",
            headers=headers,
        )
        
        if response.status_code == 200:
            return response.json()
        
        return {}

    def close(self) -> None:
        self._http.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
