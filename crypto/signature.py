from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.exceptions import InvalidSignature
 
HASH_ALGORITHM_NAME = "SHA-256"

def sign_message(private_key: RSAPrivateKey, message_bytes: bytes) -> bytes:
    return private_key.sign(message_bytes, padding.PKCS1v15(), hashes.SHA256())
 
def verify_signature(public_key: RSAPublicKey, message_bytes: bytes, signature_bytes: bytes,) -> bool:
    try:
        public_key.verify(signature_bytes, message_bytes, padding.PKCS1v15(), hashes.SHA256())
        return True
    except InvalidSignature:
        return False