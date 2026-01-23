import hashlib

def sha256_hash_bytes(data: bytes) -> str:
    hasher = hashlib.sha256()  # objeto reutilizable
    hasher.update(data)
    return hasher.hexdigest()