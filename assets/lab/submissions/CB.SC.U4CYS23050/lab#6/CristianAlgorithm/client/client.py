import socket
import time
import os
from datetime import datetime


MASTER_HOST = os.getenv("MASTER_HOST", "clock-master")
MASTER_PORT = 5000

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


def logical_time():
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime(
        "%H:%M:%S.%f"
    )[:-3]


print("==========================================")
print("       CRISTIAN'S CLOCK SYNCHRONIZATION")
print("==========================================")

print(f"Client ID       : {CLIENT_ID}")
print(f"Initial Offset  : {CLOCK_OFFSET:+.1f} seconds")

initial_time = logical_time()

print(f"Initial Clock   : {format_time(initial_time)}")
print("------------------------------------------")

try:

    # T1 - time immediately before sending request
    T1 = logical_time()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((MASTER_HOST, MASTER_PORT))

    client.sendall(b"TIME_REQUEST")

    # Receive master's time
    data = client.recv(1024)

    # T2 - time immediately after receiving response
    T2 = logical_time()

    client.close()

    master_time = float(data.decode())

    # Cristian's Algorithm
    RTT = T2 - T1
    estimated_delay = RTT / 2

    corrected_time = master_time + estimated_delay

    # Final synchronization error
    final_error = abs(corrected_time - master_time)

    print(f"T1              : {format_time(T1)}")
    print(f"Master Time     : {format_time(master_time)}")
    print(f"T2              : {format_time(T2)}")

    print("------------------------------------------")

    print(f"RTT             : {RTT * 1000:.2f} ms")
    print(f"Estimated Delay : {estimated_delay * 1000:.2f} ms")

    print("------------------------------------------")

    print(f"Corrected Clock : {format_time(corrected_time)}")
    print(f"Final Error     : {final_error * 1000:.2f} ms")

    print("==========================================")

except Exception as e:

    print(f"Synchronization failed: {e}")