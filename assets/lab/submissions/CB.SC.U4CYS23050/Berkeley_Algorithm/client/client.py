import socket
import os
import time

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
PORT = 5000


def get_clock():
    return time.time() + CLOCK_OFFSET


def format_clock(timestamp):
    return time.strftime("%H:%M:%S", time.localtime(timestamp))


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", PORT))
server.listen()

print(f"{CLIENT_ID} started")
print(f"Clock Offset: {CLOCK_OFFSET:+.1f} seconds")

while True:
    connection, address = server.accept()

    data = connection.recv(1024).decode()

    if data == "CLOCK_REQUEST":
        current_time = get_clock()

        response = str(current_time)
        connection.send(response.encode())

        print(
            f"{CLIENT_ID} → Master | "
            f"Clock: {format_clock(current_time)} "
            f"| Offset: {CLOCK_OFFSET:+.1f}s"
        )

    elif data.startswith("CORRECTION:"):
        correction = float(data.split(":")[1])

        CLOCK_OFFSET += correction

        print(
            f"{CLIENT_ID} | "
            f"Correction: {correction:+.2f}s | "
            f"New Offset: {CLOCK_OFFSET:+.2f}s"
        )

    connection.close()