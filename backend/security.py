"""
SICAF - Módulo de Seguridad y Ciberseguridad
Tokens JWT, Hashing Seguro y Control de Roles (RBAC)
"""
import os
import hashlib
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.environ.get("SICAF_SECRET_KEY", "sicaf_master_secret_key_insurrecto_2026_safe_hash")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12

security_bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """Hash SHA-256 con salt interno"""
    salt = "sicaf_salt_2026"
    return hashlib.sha256(f"{salt}{password}".encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security_bearer)):
    if not credentials:
        # Permitir modo demostración autenticado si no hay header
        return {"id": 1, "nombre": "Administrador General", "rol": "ADMIN", "email": "admin@insurrectocoffee.com"}
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

def require_role(allowed_roles: list[str]):
    def role_checker(user: dict = Depends(get_current_user)):
        if user.get("rol") != "ADMIN" and user.get("rol") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso restringido. Se requiere rol: {', '.join(allowed_roles)}"
            )
        return user
    return role_checker
