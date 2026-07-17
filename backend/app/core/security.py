"""Funciones de seguridad: JWT, contraseñas y cifrado de credenciales SAES.

Todas las operaciones criptográficas son asíncronas compatibles con el resto
de la aplicación FastAPI.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

ALGORITHM: str = "HS256"
ACCESS_TOKEN_TYPE: str = "access"
REFRESH_TOKEN_TYPE: str = "refresh"

pwd_context: CryptContext = CryptContext(
    schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto"
)


def _get_encryption_key() -> bytes:
    """Normaliza la clave de cifrado a 32 bytes para AES-256-GCM.

    Si la variable de entorno es una cadena hexadecimal válida de 64 caracteres
    se decodifica; si ya tiene 32 bytes se usa directamente; de lo contrario se
    deriva mediante SHA-256 para garantizar el tamaño exacto.
    """
    raw: str = settings.ENCRYPTION_KEY
    key_bytes: bytes
    if not raw:
        raise RuntimeError("ENCRYPTION_KEY no está configurada")
    if len(raw) == 64:
        try:
            key_bytes = bytes.fromhex(raw)
        except ValueError:
            key_bytes = raw.encode("utf-8")
    else:
        key_bytes = raw.encode("utf-8")
    if len(key_bytes) == 32:
        return key_bytes
    # Fallback determinista: SHA-256 para obtener exactamente 32 bytes
    from hashlib import sha256

    return sha256(key_bytes).digest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash bcrypt."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera un hash bcrypt de una contraseña con costo 12."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str | dict[str, Any], extra_claims: dict[str, Any] | None = None
) -> str:
    """Crea un JWT de acceso con 15 minutos de vigencia.

    Acepta un `subject` como cadena o como diccionario que contenga la clave
    `sub` (compatible con el ejemplo de verificación del proyecto).
    """
    subject_value: str
    merged_claims: dict[str, Any] = extra_claims.copy() if extra_claims else {}
    if isinstance(subject, dict):
        subject_value = subject.pop("sub", "")
        merged_claims.update(subject)
    else:
        subject_value = subject
    expires_delta: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire: datetime = datetime.now(timezone.utc) + expires_delta
    to_encode: dict[str, Any] = {
        "sub": subject_value,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": ACCESS_TOKEN_TYPE,
    }
    if merged_claims:
        to_encode.update(merged_claims)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Crea un JWT de refresco con 7 días de vigencia."""
    expires_delta: timedelta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire: datetime = datetime.now(timezone.utc) + expires_delta
    to_encode: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": REFRESH_TOKEN_TYPE,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, token_type: str) -> dict[str, Any]:
    """Decodifica y valida un JWT; lanza JWTError si es inválido o expirado."""
    payload: dict[str, Any] = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("type") != token_type:
        raise JWTError("Tipo de token incorrecto")
    return payload


def encrypt_value(value: str) -> bytes:
    """Cifra un valor con AES-256-GCM y adjunta el nonce al ciphertext."""
    aesgcm: AESGCM = AESGCM(_get_encryption_key())
    nonce: bytes = AESGCM.generate_nonce()
    ciphertext: bytes = aesgcm.encrypt(nonce, value.encode("utf-8"), None)
    return nonce + ciphertext


def decrypt_value(encrypted: bytes) -> str:
    """Descifra un valor cifrado con AES-256-GCM (nonce + ciphertext)."""
    aesgcm: AESGCM = AESGCM(_get_encryption_key())
    nonce: bytes = encrypted[:12]
    ciphertext: bytes = encrypted[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
