import socket
import threading

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from crypto.rsa_keys import RSA
from crypto.signature import sign_message
from protocol.decoder import decode_response
from protocol.encoder import (encode_get_object, encode_list_objects, encode_tamper_object, to_b64, encode_send_signed_text)
from protocol.frame import (ConnectionClosedError, FrameException, read_frame, send_frame)
from constant import (DEFAULT_HOST, DEFAULT_PORT)
class Client:
    def __init__(self):
        self.prompt = '> '
        self.socket: socket.socket = None
        self.connected: bool = False

    def welcome(self) -> None:
        print()
        print("Client started (not connected yet).")
        print("Type /help to see available commands, or /connect to connect to the server.")

    def print_help(self) -> None:
        print()
        print("=================================================================================================================")
        print("                                                 AVAILABLE COMMANDS                                              ")
        print("=================================================================================================================")
        print("** Client-local commands **")
        print()
        print("- /help                                                    - Show help")
        print("- /generate_keys <username>                                - Generate private and public key with the USERNAME")  
        print("- /exit                                                    - Disconnect and exit")
        print("- /clear                                                   - Clear the screen")
        print()
        print()
        print("** Client commands that trigger server operations **")
        print("- /send_text <username> <object_name> <message>            - Generate private and public key") 
        print("- /list                                                    - send a LIST_OBJECTS request")
        print("- /get <object_id>                                         - send a GET_OBJECT request, then verify locally")
        print("- /verify <object_id>                                      - fetch from server, then verify locally") 
        print("- /verify_all                                              - fetch list, fetch each object, then verify locally") 
        print("- /tamper <object_id>                                      - send a TAMPER_OBJECT request") 
        print()
        print("- /connect                                                - open the TCP connection")
        print("- /disconnect                                             - close the TCP connection")
        print("=================================================================================================================")
        print()

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((DEFAULT_HOST, DEFAULT_PORT))
            self.connected = True
            print(f"[+] Connected to server {DEFAULT_HOST}:{DEFAULT_PORT}")
            return True
        except (socket.error, OSError) as e:
            self.connected = False
            return False


    def close(self) -> None:                        
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self.socket.close()
                print(f"[+] Disconnecting...")
                print("[+] Disconnection successfully")
                print(f"[+] Disconnected to {DEFAULT_HOST} : {DEFAULT_PORT}")
            except OSError:
                pass
        self.connected = False
        self.socket = None


    def handle_line(self, line: str) -> None:
        if not line:
            return
        else:
            cmd, _, opt = line[1:].partition(' ')
            cmd = cmd.lower()
            if cmd == 'exit' and not opt:
                self.quit()
            elif cmd == 'help' and not opt:
                self.print_help()
                return
            elif cmd == 'connect':
                self.connect()
                return
            elif cmd == 'disconnect':
                self.close()
                return
            elif cmd == 'clear':
                self.clear_screen()
                return
            elif cmd == 'generate_keys' and len(opt.split(' ')) == 1:
                print("------------------------------")
                if self.generate_keys_for_user(opt.split(' ')[0]):
                    print(f"The key pair for {opt.split(' ')[0]} is generated")
                else:
                    print(f"Error generating a key pair for {opt.split(' ')[0]}")
                print("------------------------------")
                return
            elif cmd == 'send_text'  and len(opt.split(' ')) >= 3:
                param = opt.split(' ', 2)
                username = param[0]
                object_name = param[1]
                message_body = param[2]
                print("------------------------------")
                try:
                    res = self.send_text(username, object_name, message_body)
                    print(res)
                except Exception as e:
                    print(e)
                finally:
                    print("------------------------------")
                return
            elif cmd == 'list':
                print("------------------------------")
                try:
                    res = self.list()
                    if not res["objects"]:
                        print("No signed items")
                    else:
                        id = 1
                        for obj in res["objects"]:
                            print(f" - SIGNED OBJECT {id}:")
                            print(obj)
                            id +=1
                            print("---------")
                            print()
                except Exception as e:
                    print(e)
                finally:
                    print("------------------------------")
                return
            elif cmd == 'get' and len(opt.split(' ')) == 1 and opt.isdigit():
                print("------------------------------")
                try:
                    res = self.get(opt)
                    if not res["objects"]:
                        print("Signed object not found")
                    else:
                        print(f" - SIGNED OBJECT {opt}:")
                        print(res["objects"][0])
                        print()
                except Exception as e:
                    print(e)
                finally:
                    print("------------------------------")
                return
            elif cmd == 'tamper' and len(opt.split(' ')) == 1 and opt.isdigit():
                print("------------------------------")
                try:
                    res = self.tamper(opt)
                    if not res:
                        print(f"Signed object with ID {opt} not found")
                    else:
                        print(f" - TAMPER SIGNED OBJECT WITH ID {opt}:")
                        print()
                        print(res)
                        print("---------")
                        print(f"Signed object with ID {opt} is tampered successfully")
                except Exception as e:
                    print(e)
                finally:
                    print("------------------------------")
                return
            elif cmd == 'verify'  and not opt:
                print('[TODO] -> /verify <object_id>')
                return
            elif cmd == 'verify_all'  and not opt:
                print('[TODO] -> fetch list, fetch each object, then verify locally')
                return
            else:
                print("------------------------------")
                print(f"[*] - Command not recognized: /{cmd} {opt}")
                print("[*] - /help, showhelp")
                print("------------------------------")
                return
        
    def clear_screen(self) -> None:
        import os
        import platform
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
    
    def quit(self) -> None:
        import sys
        self.connected = False
        self.close()
        sys.exit(0)
        

    def run(self) -> None:
        self.welcome()
        while True:
            try: 
                print()
                line = input(self.prompt).strip()
            except EOFError:
                break
            self.handle_line(line)

    def generate_keys_for_user(self, username: str) -> bool:
        rsa = RSA()
        return rsa.generate_key_pair_for_username(username)

    # COMMAND: SEND_TEXT <username> <object_name> <message>
    def send_text(self, username: str, object_name: str, message_body: str):
        private_key: RSAPrivateKey = RSA.load_private_key_from_file_by_username(username) # load private key by username
        message_bytes = message_body.encode("utf-8") # encode message body as bytes UTF-8
        message_signed = sign_message(private_key, message_bytes) # sign the message bytes with the private key

        message_b64 = to_b64(message_bytes) # Base64-encode the message body
        signature_b64 = to_b64(message_signed) # Base64-encode the signature
        public_key_b64 = to_b64(RSA.public_key_to_pem(private_key.public_key()))# Base64-encode the public key

        data_to_send: tuple[bytes, dict[str, str]] = encode_send_signed_text(object_name, username, message_b64, signature_b64, public_key_b64)
        return self.send_request(data_to_send[0], data_to_send[1])
    
    # COMMAND: GET <object_id>
    def get(self, object_id: str):
        data_to_send: tuple[bytes, dict[str, str]] = encode_get_object(object_id)
        return self.send_request(data_to_send[0], data_to_send[1])
    
    # COMMAND: LIST
    def list(self):
        data_to_send: tuple[bytes, dict[str, str]] = encode_list_objects()
        return self.send_request(data_to_send[0], data_to_send[1])
    
    # COMMAND: TAMPER
    def tamper(self, object_id: str):
        data_to_send: tuple[bytes, dict[str, str]] = encode_tamper_object(object_id)
        return self.send_request(data_to_send[0], data_to_send[1])
    
    # Centralize all request/reponse in one function and DIRECTLY get the response after
    def send_request(self, msg_type: bytes, payload: dict) -> dict:
        if not self.connected:
            raise ConnectionClosedError("Not connected. Use /connect to connect to the server")

        try:
            send_frame(self.socket, msg_type, payload)
            resp_type, resp_payload = read_frame(self.socket)
            return decode_response(resp_type, resp_payload)

        except (FrameException, ConnectionClosedError) as e:
            raise Exception(f"Error on receiving response: {e}") from e

client = Client()
client.run()