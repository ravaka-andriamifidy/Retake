class MessageType:
    SUBMIT: bytes = b'S'
    LIST: bytes = b'L'
    GET: bytes = b'G'
    TAMPER: bytes = b'T'
    SUCCESS: bytes = b'O'
    ERROR: bytes = b'E'

def encode_send_signed_text():
    pass 

def encode_list_objects():
    pass 

def encode_get_object(object_id: str):
    pass 

def encode_tamper_object(object_id: str):
    pass

def encode_ok(object_id: str):
    pass

def encode_error(object_id: str):
    pass