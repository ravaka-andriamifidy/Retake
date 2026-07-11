import socket
import json
from pathlib import Path

from protocol.frame import (ConnectionClosedError, FrameException, build_frame, read_frame)
from protocol.encoder import (encode_error, encode_ok, MessageType)
from protocol.decoder import (decode_request)
from storage.object_store import (MetadataException, StorageError, get_object_by_id, store_signed_object, get_list_object, tamper)
from constant import STORAGE_DIR

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 6000
BUFFER_SIZE = 4096

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((DEFAULT_HOST, DEFAULT_PORT))

# Listen for incoming connections
s.listen(5)

print(f"Server started on {DEFAULT_HOST}:{DEFAULT_PORT}")
print("Waiting for clients...")
print()

while True:
    # Accept a connection
    conn, addr = s.accept()
    print(f"> Connected by {addr}")
    print()
    while True:
        try:
            msg_type, payload = read_frame(conn)
            
            if msg_type == MessageType.SUBMIT:
                signed_object: dict = decode_request(msg_type, payload)
                # store the signed_object in the "server_storage" folder
                store_signed_object(signed_object)
                type, response = encode_ok(signed_object) 
                resp_bytes= build_frame(type, response)
                conn.sendall(resp_bytes) # send the response to the client
                
            if msg_type == MessageType.GET:
                object_id_request : dict = decode_request(msg_type, payload)
                object_result = get_object_by_id(object_id_request["object_id"])
                type, response = encode_ok({"object": object_result["object"]})
                resp_bytes= build_frame(type, response)
                conn.sendall(resp_bytes) # send the response to the client

            if msg_type == MessageType.LIST:
                objects = get_list_object()
                type, response = encode_ok({"objects": objects["objects"]})
                resp_bytes= build_frame(type, response)
                conn.sendall(resp_bytes) # send the response to the client

            if msg_type == MessageType.TAMPER:
                object_id_request : dict = decode_request(msg_type, payload)
                object_tampered: dict = tamper(object_id_request["object_id"])
                type, response = encode_ok({"object": object_tampered})
                resp_bytes= build_frame(type, response)
                conn.sendall(resp_bytes) # send the response to the client

        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            resp_bytes= build_frame(MessageType.ERROR, encode_error(f"UnicodeDecodeError-JSONDecodeError: {e}")[1])
            conn.sendall(resp_bytes)
        except StorageError as e:
            resp_bytes= build_frame(MessageType.ERROR, encode_error("Storage error: {e}")[1])
            conn.sendall(resp_bytes)
        except  ConnectionClosedError as e:
            resp_bytes= build_frame(MessageType.ERROR, encode_error(f"Connection error: {e}")[1])
            conn.sendall(resp_bytes)
            break
        except (FrameException) as e:
            resp_bytes= build_frame(MessageType.ERROR, encode_error(f"Frame exception: {e}")[1])
            conn.sendall(resp_bytes)
            break
        except FileExistsError as e:
            resp_bytes= build_frame(MessageType.ERROR, encode_error(f"Folder already exists: {e}")[1])
            conn.sendall(resp_bytes)
            break
        except PermissionError as e:
            resp_bytes= build_frame(MessageType.ERROR, encode_error(f"Permission denied: {e}")[1])
            conn.sendall(resp_bytes)
        except MetadataException as e:
            resp_bytes= build_frame(MessageType.ERROR, encode_error(f"Metadata error: {e}")[1])
            conn.sendall(resp_bytes)
        except OSError as e:
            resp_bytes= build_frame(MessageType.ERROR, encode_error("System error: {e}")[1])
            conn.sendall(resp_bytes)
            break
        except Exception as e:
            resp_bytes= build_frame(MessageType.ERROR, encode_error(f"Unexpected error: {e}")[1])
            conn.sendall(resp_bytes)
            break