"""
Wealthsimple OAuth Authentication
Handles token management and session renewal
"""
from __future__ import annotations

import json
import time
import webbrowser
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass
import requests


@dataclass
class TokenData:
    """OAuth token data"""
    access_token: str
    refresh_token: str
    expires_at: float
    scope: str


class WealthsimpleAuth:
    """
    Wealthsimple OAuth Authentication Handler
    Handles the OAuth2 flow for Wealthsimple Trade API
    """

    # Wealthsimple API endpoints
    AUTH_URL = "https://api.wealthsimple.com/oauth/authorize"
    TOKEN_URL = "https://api.wealthsimple.com/oauth/token"
    TOKEN_REFRESH_URL = "https://api.wealthsimple.com/oauth/token"
    BASE_URL = "https://trade-api.wealthsimple.com"

    def __init__(self, client_id: str = None, client_secret: str = None,
                 redirect_uri: str = "http://localhost:8080/callback",
                 token_file: Path = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_file = token_file or Path("wealthsimple_tokens.json")
        self._token_data: Optional[TokenData] = None

    def get_auth_url(self) -> str:
        """Get OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read write trade",
            "state": self._generate_state()
        }
        return f"{self.AUTH_URL}?{self._urlencode(params)}"

    def start_auth_flow(self) -> str:
        """Start OAuth flow by opening browser"""
        url = self.get_auth_url()
        print(f"\nOpening browser for authorization...")
        print(f"If browser doesn't open, visit: {url}\n")
        webbrowser.open(url)
        return url

    def exchange_code(self, auth_code: str) -> TokenData:
        """Exchange authorization code for tokens"""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "redirect_uri": self.redirect_uri
        }

        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()
        token_json = response.json()

        token_data = TokenData(
            access_token=token_json["access_token"],
            refresh_token=token_json.get("refresh_token", ""),
            expires_at=time.time() + token_json.get("expires_in", 3600),
            scope=token_json.get("scope", "")
        )

        self._token_data = token_data
        self._save_tokens(token_data)
        return token_data

    def refresh_token(self) -> TokenData:
        """Refresh access token using refresh token"""
        if not self._token_data or not self._token_data.refresh_token:
            raise Exception("No refresh token available")

        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self._token_data.refresh_token
        }

        response = requests.post(self.TOKEN_REFRESH_URL, data=data)
        response.raise_for_status()
        token_json = response.json()

        token_data = TokenData(
            access_token=token_json["access_token"],
            refresh_token=token_json.get("refresh_token", self._token_data.refresh_token),
            expires_at=time.time() + token_json.get("expires_in", 3600),
            scope=token_json.get("scope", self._token_data.scope)
        )

        self._token_data = token_data
        self._save_tokens(token_data)
        return token_data

    def get_access_token(self) -> str:
        """Get valid access token (refresh if needed)"""
        if self._token_data is None:
            self._token_data = self._load_tokens()

        if self._token_data is None:
            raise Exception("Not authenticated. Run start_auth_flow()")

        # Check if token needs refresh
        if time.time() >= self._token_data.expires_at - 60:  # Refresh 1 min early
            self.refresh_token()

        return self._token_data.access_token

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        try:
            self.get_access_token()
            return True
        except:
            return False

    def _save_tokens(self, token_data: TokenData):
        """Save tokens to file"""
        with open(self.token_file, 'w') as f:
            json.dump({
                "access_token": token_data.access_token,
                "refresh_token": token_data.refresh_token,
                "expires_at": token_data.expires_at,
                "scope": token_data.scope
            }, f)

    def _load_tokens(self) -> Optional[TokenData]:
        """Load tokens from file"""
        if not self.token_file.exists():
            return None

        with open(self.token_file) as f:
            data = json.load(f)

        return TokenData(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", ""),
            expires_at=data.get("expires_at", 0),
            scope=data.get("scope", "")
        )

    def logout(self):
        """Clear authentication"""
        self._token_data = None
        if self.token_file.exists():
            self.token_file.unlink()

    def _generate_state(self) -> str:
        """Generate random state for OAuth"""
        import secrets
        return secrets.token_urlsafe(32)

    def _urlencode(self, params: Dict) -> str:
        """URL encode parameters"""
        from urllib.parse import urlencode
        return urlencode(params)


class WealthsimpleAuthManager:
    """
    Manages authentication for multiple Wealthsimple accounts
    Useful for managing personal and business accounts
    """

    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path("data/wealthsimple")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._auths: Dict[str, WealthsimpleAuth] = {}

    def add_account(self, name: str, client_id: str, client_secret: str) -> WealthsimpleAuth:
        """Add a new Wealthsimple account"""
        token_file = self.config_dir / f"{name}_tokens.json"
        auth = WealthsimpleAuth(client_id, client_secret, token_file=token_file)
        self._auths[name] = auth
        return auth

    def get_account(self, name: str) -> WealthsimpleAuth:
        """Get auth handler for named account"""
        if name not in self._auths:
            # Try to load from config
            config_file = self.config_dir / f"{name}_config.json"
            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)
                auth = WealthsimpleAuth(
                    client_id=config.get("client_id"),
                    client_secret=config.get("client_secret"),
                    token_file=self.config_dir / f"{name}_tokens.json"
                )
                self._auths[name] = auth
            else:
                raise Exception(f"Account '{name}' not found")

        return self._auths[name]

    def list_accounts(self) -> list:
        """List all configured accounts"""
        configs = self.config_dir.glob("*_config.json")
        return [c.stem.replace("_config", "") for c in configs]

    def remove_account(self, name: str):
        """Remove an account"""
        if name in self._auths:
            self._auths[name].logout()
            del self._auths[name]

        # Clean up files
        config_file = self.config_dir / f"{name}_config.json"
        token_file = self.config_dir / f"{name}_tokens.json"
        if config_file.exists():
            config_file.unlink()
        if token_file.exists():
            token_file.unlink()
