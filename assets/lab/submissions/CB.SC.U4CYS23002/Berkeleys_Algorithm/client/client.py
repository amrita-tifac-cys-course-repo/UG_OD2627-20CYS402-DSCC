import socket
import time
import os
from datetime import datetime


SERVER_HOST = os.getenv("SERVER_HOST", "server")
SERVER_PORT = 5000

CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


def get_time():
    return time.time() + CLOCK_OFFSET

def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )

def main():
    global CLOCK_OFFSET
    
    current_time = get_time()
    print(f"[CLIENT] Current time: {format_time(current_time)}")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))

    client.sendall(str(current_time).encode())
    print(f"[CLIENT] Sent time: {format_time(current_time)}")

    data = client.recv(1024).decode().strip()
    delay_str, ref_time_str = data.split(",")

    delay = float(delay_str)
    ref_time = float(ref_time_str)

    print(f"[CLIENT] Received correction: {delay:+.3f} seconds")

    CLOCK_OFFSET += delay

    new_time = get_time()
    error = abs(ref_time - new_time)

    print(f"[CLIENT] New time: {format_time(new_time)}")
    print(f"[CLIENT] Reference time: {format_time(ref_time)}")
    print(f"[CLIENT] Synchronization error: {error:.6f} seconds")
    print(f"[CLIENT] Synchronization error: {error * 1000:.3f} ms")

    client.close()

if __name__ == "__main__":
    main()
