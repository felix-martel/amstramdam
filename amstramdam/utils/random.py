import random
import string

CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase


def generate_random_identifier(length: int) -> str:
    """Generate a random alphanumeric identifier of given length"""
    return "".join(random.choices(CHARS, k=length))
