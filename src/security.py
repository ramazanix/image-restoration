import subprocess
from passlib.context import CryptContext
from hashlib import shake_256


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)


def get_password_hash(raw_password: str) -> str:
    return pwd_context.hash(raw_password)


def hash_file_name(filename: str):
    return shake_256(filename.encode()).hexdigest(8)


def process_images(file_dir: str):
    user_id = file_dir.split('/')[-1]
    commands = ['python', 'run.py', '--input_folder', file_dir, '--output_folder',
                f'/data/user_images/{user_id}', '--GPU', '-1', '--with_scratch']
    proc = subprocess.Popen(commands, cwd='/image-restoration/neural_link')
    proc.wait()
