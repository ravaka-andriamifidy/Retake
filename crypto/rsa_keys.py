
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives import serialization
from constant import KEY_DIR
 
RSA_KEY_SIZE = 2048
RSA_PUBLIC_EXPONENT = 65537

class RSA:
    def __init__(self):
        self.private_key: RSAPrivateKey = None
        self.public_key: RSAPublicKey = None

    def generate_key_pair(self) -> None:
        # Generate private key
        self.private_key =  rsa.generate_private_key(
            public_exponent=RSA_PUBLIC_EXPONENT, 
            key_size=RSA_KEY_SIZE
        )
        # Generate Public Key from private key
        self.public_key = self.private_key.public_key()
        
    def generate_key_pair_for_username(self, username: str) -> bool:
        self.generate_key_pair() # Generate key pair
        if self.private_key and self.public_key:
            # create the folder or not if it already exists
            path = Path(KEY_DIR)
            path.mkdir(parents=True, exist_ok=True)
            with open(path / f"{username}_private.pem", "wb") as f:
                f.write(self.private_key_to_pem(self.private_key))
            with open(path / f"{username}_public.pub", "wb") as f:
                f.write(self.public_key_to_pem(self.public_key))
            return True
        else:
            return False
        
    def private_key_to_pem(private_key: RSAPrivateKey) -> bytes:
        if private_key: # Check whether the private key is set
            return private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        else:
            return None
        
    @staticmethod
    def public_key_to_pem(public_key: RSAPublicKey) -> bytes:
        if public_key: # Check whether the public key is set
            return public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        else:
            return None
        
    @staticmethod
    def load_private_key_from_file_by_username(username: str) -> RSAPrivateKey: # for public key, we have just to 
        private_path = Path(KEY_DIR) / f"{username}_private.pem" # absolute path to private key

        if not private_path.exists():
            raise FileNotFoundError(f"No private key found for ‘{username}’ in {KEY_DIR}/ folder.")
        with open(private_path, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    