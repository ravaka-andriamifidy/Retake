import socket
import threading

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 6000
BUFFER_SIZE = 4096


class Client:
    def __init__(self):
        self.prompt = '> '
        self.socket: socket.socket = None
        self._listener: threading.Thread = None
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
            self._listener = threading.Thread(target=self.receiver, daemon=True)
            self._listener.start()
            self.connected = True
            print(f"[+] Connected to server {DEFAULT_HOST}:{DEFAULT_PORT}")
            return True
        except (socket.error, OSError) as e:
            self.connected = False
            return False


    def receiver(self):
        while self.connected:
            self.socket.settimeout(0.5)
            try:
                data = self.socket.recv(BUFFER_SIZE)
                if not data:
                    self.connected = False
                    self.close()
                    break
            except socket.timeout:
                continue
            except (socket.error, OSError) as e:
                self.connected = False
                self.close()
                break


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
        self.socket = None


    def handle_line(self, line: str) -> None:
        if not line:
            return
        else:
            cmd, _, opt = line[1:].partition(' ')
            cmd = cmd.lower()
            if cmd in ('quit', 'exit') and not opt:
                self.quit()
            elif cmd == 'help'  and not opt:
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
            elif cmd == 'send_text':
                print('[TODO] -> send signed object')
                return
            elif cmd == 'list':
                print('[TODO] -> /get <object_id>')
                return
            elif cmd == 'get':
                print('[TODO] -> get one object (request/response)"')
                return
            elif cmd == 'verify'  and not opt:
                print('[TODO] -> /verify <object_id>')
                return
            elif cmd == 'verify_all'  and not opt:
                print('[TODO] -> fetch list, fetch each object, then verify locally')
                return
            else:
                print(f"[!] - Command not recognized: /{cmd} {opt}")
                print("[+] - /help, Showhelp")
                return
        
    def clear_screen(self) -> None:
        import os
        import platform
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
        

    def run(self) -> None:
        self.welcome()
        while True:
            try: 
                print()
                line = input(self.prompt).strip()
            except EOFError:
                break
            self.handle_line(line)

client = Client()
client.run()