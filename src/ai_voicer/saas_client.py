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
        """Check if user is logged in with valid token."""
        creds = self._load_credentials()
        return creds.is_logged_in()
    
    def get_access_token(self) -> Optional[str]:
        """Get valid access token, refreshing if needed."""
        creds = self._load_credentials()
        
        if not creds.access_token:
            return None
        
        if creds.is_expired() and creds.refresh_token:
            # Try to refresh
            if self._refresh_token(creds):
                creds = self._load_credentials()
            else:
                return None
        
        return creds.access_token
    
    def _refresh_token(self, creds: SaasCredentials) -> bool:
        """Refresh access token using refresh token."""
        if not creds.refresh_token:
            return False
        
        try:
            response = httpx.post(
                f"{self.backend_url}/v1/auth/refresh",
                json={"refresh_token": creds.refresh_token},
                timeout=30.0
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
            response = httpx.post(
                f"{self.backend_url}/v1/auth/login",
                json={"email": email, "password": password},
                timeout=30.0
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
                httpx.post(
                    f"{self.backend_url}/v1/auth/logout",
                    headers=self.get_auth_headers(),
                    json={"refresh_token": creds.refresh_token},
                    timeout=10.0
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


class SaasTranscriptionService:
    """Transcription service that uses SaaS API with auth."""
    
    def __init__(self, backend_url: str, auth_manager: Optional[SaasAuthManager] = None):
        self.backend_url = backend_url.rstrip("/")
        self.auth = auth_manager or SaasAuthManager(backend_url)
    
    def transcribe_and_structure_file(self, audio_path: str) -> Tuple[str, str]:
        """Transcribe audio file using SaaS API."""
        if not self.auth.is_logged_in():
            raise RuntimeError(
                "Not logged in. Run: python run_saas_daemon.py login <email>"
            )
        
        headers = self.auth.get_auth_headers()
        
        with open(audio_path, "rb") as file_obj:
            files = {"audio": (os.path.basename(audio_path), file_obj, "audio/wav")}
            response = httpx.post(
                f"{self.backend_url}/v1/transcribe",
                headers=headers,
                files=files,
                params={"structured": "true"},
                timeout=120.0
            )
        
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
        
        return transcript, text
    
    def get_usage(self) -> dict:
        """Get current usage stats."""
        headers = self.auth.get_auth_headers()
        
        response = httpx.get(
            f"{self.backend_url}/v1/usage/current-period",
            headers=headers,
            timeout=30.0
        )
        
        if response.status_code == 200:
            return response.json()
        
        return {}
