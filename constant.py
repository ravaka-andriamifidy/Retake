from protocol.encoder import MessageType

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 6000
BUFFER_SIZE = 4096

STORAGE_DIR = "server_storage"
KEY_DIR = "keys"

TYPE_TO_COMMAND = {
    MessageType.SUBMIT: "SEND_SIGNED_TEXT",
    MessageType.LIST: "LIST_OBJECTS",
    MessageType.GET: "GET_OBJECT",
    MessageType.TAMPER: "TAMPER_OBJECT",
}

REQUIRED_FIELDS = {
    "SEND_SIGNED_TEXT": [
        "object_name",
        "sender",
        "message_b64",
        "signature_b64",
        "public_key_b64",
        "hash_algorithm",
    ],
    "LIST_OBJECTS": [],
    "GET_OBJECT": ["object_id"],
    "TAMPER_OBJECT": ["object_id"],
}

REQUIRED_METADATA_FIELDS: dict[str, type] = {
    "object_id": int,
    "object_name": str,
    "sender": str,
    "hash_algorithm": str,
    "timestamp": str,
    "tampered": bool,
}