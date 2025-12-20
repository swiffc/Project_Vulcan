"""
Auth Adapter - JWT/OAuth Authentication

Thin wrapper for authentication and authorization.
Supports JWT tokens and OAuth2 flows.
"""

import os
import logging
import secrets
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger("core.auth")


@dataclass
class AuthConfig:
    """Authentication configuration."""
    secret_key: str = None
    algorithm: str = "HS256"
    token_expiry_hours: int = 24
    refresh_expiry_days: int = 7

    def __post_init__(self):
        if self.secret_key is None:
            self.secret_key = os.getenv("JWT_SECRET", secrets.token_hex(32))


@dataclass
class TokenPayload:
    """JWT token payload."""
    user_id: str
    email: Optional[str] = None
    roles: list = None
    exp: datetime = None
    iat: datetime = None

    def to_dict(self) -> Dict:
        return {
            "sub": self.user_id,
            "email": self.email,
            "roles": self.roles or [],
            "exp": self.exp.timestamp() if self.exp else None,
            "iat": self.iat.timestamp() if self.iat else None,
        }


class AuthAdapter:
    """
    Authentication adapter for JWT and OAuth.

    Supports:
    - JWT token creation/validation
    - Refresh tokens
    - Role-based access control
    - OAuth2 token exchange (Google, GitHub)
    """

    def __init__(self, config: AuthConfig = None):
        self.config = config or AuthConfig()
        self._jwt = None
        self._refresh_tokens: Dict[str, str] = {}

    def _init_jwt(self):
        """Lazy load JWT library."""
        if self._jwt is None:
            try:
                import jwt
                self._jwt = jwt
            except ImportError:
                raise RuntimeError("PyJWT not installed. Run: pip install pyjwt")

    def create_token(self, user_id: str, email: str = None, roles: list = None) -> str:
        """
        Create JWT access token.

        Args:
            user_id: Unique user identifier
            email: Optional email
            roles: Optional role list

        Returns:
            Encoded JWT string
        """
        self._init_jwt()

        now = datetime.utcnow()
        payload = TokenPayload(
            user_id=user_id,
            email=email,
            roles=roles or ["user"],
            iat=now,
            exp=now + timedelta(hours=self.config.token_expiry_hours)
        )

        token = self._jwt.encode(
            payload.to_dict(),
            self.config.secret_key,
            algorithm=self.config.algorithm
        )

        logger.info(f"Created token for user: {user_id}")
        return token

    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token for user."""
        refresh = secrets.token_urlsafe(32)
        self._refresh_tokens[refresh] = user_id
        return refresh

    def validate_token(self, token: str) -> Optional[TokenPayload]:
        """
        Validate JWT token.

        Returns:
            TokenPayload if valid, None otherwise
        """
        self._init_jwt()

        try:
            payload = self._jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm]
            )

            return TokenPayload(
                user_id=payload.get("sub"),
                email=payload.get("email"),
                roles=payload.get("roles", []),
                exp=datetime.fromtimestamp(payload.get("exp", 0)),
                iat=datetime.fromtimestamp(payload.get("iat", 0))
            )

        except self._jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except self._jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Exchange refresh token for new access token."""
        user_id = self._refresh_tokens.get(refresh_token)
        if user_id:
            return self.create_token(user_id)
        return None

    def revoke_refresh_token(self, refresh_token: str):
        """Revoke a refresh token."""
        self._refresh_tokens.pop(refresh_token, None)

    def check_role(self, payload: TokenPayload, required_role: str) -> bool:
        """Check if user has required role."""
        return required_role in (payload.roles or [])

    async def exchange_oauth_code(
        self,
        provider: str,
        code: str,
        redirect_uri: str
    ) -> Optional[Dict[str, Any]]:
        """
        Exchange OAuth authorization code for tokens.

        Args:
            provider: "google" or "github"
            code: Authorization code
            redirect_uri: Callback URL

        Returns:
            User info dict or None
        """
        try:
            import httpx
        except ImportError:
            raise RuntimeError("httpx not installed. Run: pip install httpx")

        if provider == "google":
            return await self._exchange_google(code, redirect_uri)
        elif provider == "github":
            return await self._exchange_github(code)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _exchange_google(self, code: str, redirect_uri: str) -> Optional[Dict]:
        """Exchange Google OAuth code."""
        import httpx

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        async with httpx.AsyncClient() as client:
            # Exchange code for token
            resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            tokens = resp.json()

            # Get user info
            resp = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            return resp.json()

    async def _exchange_github(self, code: str) -> Optional[Dict]:
        """Exchange GitHub OAuth code."""
        import httpx

        client_id = os.getenv("GITHUB_CLIENT_ID")
        client_secret = os.getenv("GITHUB_CLIENT_SECRET")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret
                },
                headers={"Accept": "application/json"}
            )
            tokens = resp.json()

            resp = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            return resp.json()


def require_auth(auth: AuthAdapter, roles: list = None):
    """Decorator requiring authentication."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            token = kwargs.get("token") or (args[0] if args else None)
            if not token:
                raise AuthError("No token provided")

            payload = auth.validate_token(token)
            if not payload:
                raise AuthError("Invalid or expired token")

            if roles and not any(auth.check_role(payload, r) for r in roles):
                raise AuthError("Insufficient permissions")

            kwargs["user"] = payload
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class AuthError(Exception):
    """Authentication error."""
    pass


# Singleton
_auth: Optional[AuthAdapter] = None


def get_auth_adapter(config: AuthConfig = None) -> AuthAdapter:
    """Get or create auth adapter singleton."""
    global _auth
    if _auth is None:
        _auth = AuthAdapter(config)
    return _auth
