import socket

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 6000
BUFFER_SIZE = 4096

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((DEFAULT_HOST, DEFAULT_PORT))

# Listen for incoming connections
s.listen(5)

while True:
    print(f"Server started on {DEFAULT_HOST}:{DEFAULT_PORT}")
    print("Waiting for clients...")
    print()
    # Accept a connection
    conn, addr = s.accept()
    print(f"> Connected by {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        conn.sendall(data)