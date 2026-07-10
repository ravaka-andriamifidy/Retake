import base64

class MessageType:
    SUBMIT: bytes = b'S'
    LIST: bytes = b'L'
    GET: bytes = b'G'
    TAMPER: bytes = b'T'
    OK: bytes = b'O'
    ERROR: bytes = b'E'

def encode_send_signed_text(object_name: str, sender: str, message_b64: str, signature_b64: str, public_key_b64: str, hash_algorithm: str = "SHA-256"):
    payload = {
        "command": "SEND_SIGNED_TEXT",
        "object_name": object_name,
        "sender": sender,
        "message_b64": message_b64,
        "signature_b64": signature_b64,
        "public_key_b64": public_key_b64,
        "hash_algorithm": hash_algorithm,
    }
    return MessageType.SUBMIT, payload 

def encode_list_objects():
    payload = {
        "command": "LIST_OBJECTS",
    }
    return MessageType.LIST, payload  

def encode_get_object(object_id: str):
    pass 

def encode_tamper_object(object_id: str):
    pass

def encode_ok(message: str) -> tuple[bytes, dict]:
    payload = {
        "status": "OK",
        "message": message,
    }
    return MessageType.OK, payload
 

def encode_error(message: str) -> tuple[bytes, dict]:
    payload = {
        "status": "ERROR",
        "message": message,
    }
    return MessageType.ERROR, payload

def to_b64(data: bytes) -> str: # bytes to string
    return base64.b64encode(data).decode("ascii")
 
def from_b64(text: str) -> bytes: # string to bytes
    return base64.b64decode(text.encode("ascii"))