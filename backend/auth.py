from typing import Optional, List
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import functions

# HTTPBearer enables the Swagger UI "Authorize" button and extracts Bearer tokens
security = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """
    Extracts and verifies JWT from:
    1. Standard 'Authorization: Bearer <token>' header (via HTTPBearer)
    2. 'token' custom header (for backwards compatibility)
    """
    token: Optional[str] = None
    if auth_credentials and auth_credentials.credentials:
        token = auth_credentials.credentials
    elif "token" in request.headers:
        token = request.headers["token"]
    elif "authorization" in request.headers:
        auth_hdr = request.headers["authorization"]
        if auth_hdr.startswith("Bearer "):
            token = auth_hdr[7:].strip()
        else:
            token = auth_hdr.strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required. Provide 'Authorization: Bearer <token>' or 'token' header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = functions.verify_token_payload(token=token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub") or payload.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing user identity",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = functions.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_roles(*allowed_roles: str):
    """
    Role-Based Access Control (RBAC) dependency factory.
    Verifies that the authenticated user possesses one of the allowed roles.
    """
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "staff")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access forbidden: requires one of the following roles: {list(allowed_roles)}. "
                    f"Your current role is '{user_role}'."
                ),
            )
        return current_user

    return role_checker


# Convenient role dependencies for FastAPI routes
RequireAdmin = Depends(require_roles("admin"))
RequireManager = Depends(require_roles("admin", "manager"))
RequireStaff = Depends(require_roles("admin", "manager", "staff"))
RequireAuth = Depends(get_current_user)
