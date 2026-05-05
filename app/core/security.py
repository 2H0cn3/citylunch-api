import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_SPECIAL_CHARS = "!@#$%&*"


def generate_random_password(length: int = 12) -> str:
    """Génère un mot de passe aléatoire sécurisé.

    Garantit au moins une minuscule, une majuscule, un chiffre, un caractère spécial.
    """
    if length < 8:
        raise ValueError("La longueur minimale est 8 caractères.")

    alphabet = string.ascii_letters + string.digits + _SPECIAL_CHARS
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in _SPECIAL_CHARS for c in password)
        ):
            return password


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str, expires_minutes: Optional[int] = None
) -> str:
    expires_delta = timedelta(
        minutes=expires_minutes or settings.JWT_EXPIRATION_MINUTES
    )
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": str(subject), "exp": expire}
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        return None