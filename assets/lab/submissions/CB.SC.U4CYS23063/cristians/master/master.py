import socket
import time
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000

# Artificial delay in milliseconds
DELAY_MS = int(os.getenv("DELAY_MS", "0"))

print("=" * 60)
print("        CRISTIAN'S CLOCK - MASTER TIME SERVER")
print("=" * 60)
print(f"Server Port       : {PORT}")
print(f"Artificial Delay  : {DELAY_MS} ms")
print("=" * 60)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(10)

print("Master server is running...")
print("Waiting for client requests...\n")

while True:
    conn, address = server.accept()

    try:
        request = conn.recv(1024).decode().strip()

        print(f"[REQUEST] Client {address} -> {request}")

        if request == "TIME_REQUEST":

            # Half of artificial delay before generating timestamp
            time.sleep(DELAY_MS / 2000)

            # Master's current logical time
            master_time = time.time()

            # Remaining half of artificial delay
            time.sleep(DELAY_MS / 2000)

            response = f"{master_time:.9f}"

            conn.sendall(response.encode())

            readable_time = datetime.fromtimestamp(master_time).strftime(
                "%H:%M:%S.%f"
            )[:-3]

            print(
                f"[RESPONSE] Master Time = {readable_time} "
                f"| Delay = {DELAY_MS} ms"
            )

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        conn.close()