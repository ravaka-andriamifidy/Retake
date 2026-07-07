import struct
import json
import socket

HEADER = b"SFX"
HEADER_SIZE = 3
TYPE_SIZE = 1
LENGTH_SIZE = 4
FIXED_PART_SIZE = len(HEADER) + TYPE_SIZE + LENGTH_SIZE
MAX_PAYLOAD = 1_048_576  # 1 MiB

class FrameError(Exception):
    pass

class Frame():
    def __init__(self, header, type, payload):
        self.header = header
        self.type = type
        self.payload = payload
        self.length = len(payload)

    def build_frame(msg_type: bytes, payload_dict: dict) -> bytes:
        payload_bytes = json.dumps(payload_dict).encode("utf-8")
        length_bytes = struct.pack(">I", len(payload_bytes))
        return HEADER + msg_type + length_bytes + payload_bytes