from passlib.context import CryptContext
from hashlib import shake_256


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)


def get_password_hash(raw_password: str) -> str:
    return pwd_context.hash(raw_password)


def hash_file_name(filename: str):
    return shake_256(filename.encode()).hexdigest(8)
