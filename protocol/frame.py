import struct
import json
import socket

HEADER = b"SFX"
HEADER_SIZE: bytes = 3
TYPE_SIZE: bytes = 1
LENGTH_SIZE: bytes = 4
FIXED_PART_SIZE: bytes = len(HEADER) + TYPE_SIZE + LENGTH_SIZE
MAX_PAYLOAD = 1_048_576

class FrameException(Exception):
    pass

class ConnectionClosedError(Exception): 
    pass

def build_frame(msg_type: bytes, payload_dict: dict) -> bytes: # for the client
    payload = json.dumps(payload_dict).encode("utf-8")
    length_bytes = struct.pack(">I", len(payload))
    return HEADER + msg_type + length_bytes + payload

def read_frame(socket: socket.socket) -> tuple[int, dict]: # for the server
    received_data = received_packet(socket, FIXED_PART_SIZE)
    header = received_data[0:3] 

    if header != HEADER:
        raise FrameException(f"Invalid HEADER")

    msg_type = received_data[3:4]

    length_bytes = received_data[4:8]
    length, = struct.unpack(">I", length_bytes)

    if length > MAX_PAYLOAD:
        raise FrameException(f"Payload too large  : {length} > {MAX_PAYLOAD} octets")

    payload_bytes = received_packet(socket, length)

    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise FrameException(f"Invalid JSON : {e}")

    return msg_type, payload

def send_frame(sock: socket.socket, msg_type: bytes, payload_dict: dict) -> None:
    frame = build_frame(msg_type, payload_dict)
    sock.sendall(frame)

def received_packet(sock: socket.socket, n: int) -> bytes:
    data = bytearray()
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionClosedError("Connection closed")
        data.extend(chunk)
    return bytes(data)