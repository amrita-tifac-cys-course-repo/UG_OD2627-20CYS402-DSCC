import socket
import time
import os
from datetime import datetime


HOST = "0.0.0.0"
PORT = 5000

# Artificial delay in milliseconds
DELAY_MS = int(os.getenv("DELAY_MS", "0"))


def get_logical_time():
    return time.time()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(10)

print("========================================")
print("     CRISTIAN'S CLOCK TIME SERVER")
print("========================================")
print(f"Server listening on port {PORT}")
print(f"Artificial delay: {DELAY_MS} ms")
print("Waiting for clients...\n")


while True:

    conn, address = server.accept()

    try:
        request = conn.recv(1024).decode()

        if request == "TIME_REQUEST":

            print(f"Request received from {address}")

            # Artificial processing delay
            if DELAY_MS > 0:
                time.sleep(DELAY_MS / 1000)

            master_time = get_logical_time()

            response = str(master_time)

            conn.sendall(response.encode())

            readable_time = datetime.fromtimestamp(master_time)

            print(f"Master Time: {readable_time}")
            print("----------------------------------------")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        conn.close()