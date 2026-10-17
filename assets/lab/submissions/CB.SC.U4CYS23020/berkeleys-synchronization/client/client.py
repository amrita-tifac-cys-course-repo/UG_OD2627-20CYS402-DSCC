import socket
import os
import time

CLIENT_ID = os.environ.get("CLIENT_ID", "Client")
CLOCK_OFFSET = float(os.environ.get("CLOCK_OFFSET", "0"))
PORT = 5000

def start_server():
    global CLOCK_OFFSET
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PORT))
    server.listen(5)
    print(f"[{CLIENT_ID}] Started with offset {CLOCK_OFFSET}s. Listening on port {PORT}...")

    while True:
        client_sock, addr = server.accept()
        data = client_sock.recv(1024).decode('utf-8')
        if data == "CLOCK_REQUEST":
            simulated_time = time.time() + CLOCK_OFFSET
            client_sock.send(str(simulated_time).encode('utf-8'))
            
            correction_data = client_sock.recv(1024).decode('utf-8')
            if correction_data.startswith("CORRECTION:"):
                correction = float(correction_data.split(":")[1])
                print(f"[{CLIENT_ID}] Received correction: {correction} sec")
                CLOCK_OFFSET += correction
                client_sock.send("OK".encode('utf-8'))
        client_sock.close()

if __name__ == "__main__":
    start_server()
