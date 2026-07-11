from .frame import FrameException
from .encoder import MessageType
from constant import (TYPE_TO_COMMAND, REQUIRED_FIELDS)


def decode_request(msg_type: bytes, payload: dict) -> dict:
    if msg_type not in TYPE_TO_COMMAND:
        raise FrameException(f"Unknown type")

    expected_command = TYPE_TO_COMMAND[msg_type]
    command = payload.get("command")

    if command != expected_command:
        raise FrameException("Unsupported command")

    required = REQUIRED_FIELDS[expected_command]
    missing = [field for field in required if field not in payload]
    if missing:
        raise FrameException(
            f"Missing mandatory fields"
        )
    return payload


def decode_response(msg_type: bytes, payload: dict) -> dict:
    if msg_type == MessageType.OK:
        if payload.get("status") != "OK" and payload.get("message") is None:
            raise FrameException("Unknown response type")

    if msg_type == MessageType.ERROR:
        if payload.get("status") != "ERROR" and payload.get("message") is None:
            raise FrameException("Unknown response type")
    return payload