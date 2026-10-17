import socket
import os
import time

PORT = 5000
ARTIFICIAL_DELAY = float(os.environ.get("ARTIFICIAL_DELAY", "0"))

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PORT))
    server.listen(5)
    print(f"Master Time Server started. Listening on port {PORT} with {ARTIFICIAL_DELAY}s delay.")

    while True:
        client_sock, addr = server.accept()
        data = client_sock.recv(1024).decode('utf-8')
        if data == "TIME_REQUEST":
            print(f"Received TIME_REQUEST from {addr}")
            if ARTIFICIAL_DELAY > 0:
                time.sleep(ARTIFICIAL_DELAY)
            
            master_time_str = str(time.time())
            client_sock.send(master_time_str.encode('utf-8'))
        client_sock.close()

if __name__ == "__main__":
    start_server()
