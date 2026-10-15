import socket
import time
import os
from datetime import datetime

MASTER_HOST = os.getenv("MASTER_HOST", "clock-master")
MASTER_PORT = int(os.getenv("MASTER_PORT", "5000"))

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

SYNC_INTERVAL = 5

# ---------------------------------------------------------
# Logical clock
# ---------------------------------------------------------

def logical_time():
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime(
        "%H:%M:%S.%f"
    )[:-3]


# ---------------------------------------------------------
# Synchronization
# ---------------------------------------------------------

def synchronize():

    print("\n" + "=" * 60)
    print("        CRISTIAN'S CLOCK SYNCHRONIZATION")
    print("=" * 60)

    print(f"Client ID       : {CLIENT_ID}")
    print(f"Clock Offset    : {CLOCK_OFFSET:+.1f} seconds")
    print(f"Initial Clock   : {format_time(logical_time())}")

    # -----------------------------------------------------
    # T1 - Time immediately before request
    # -----------------------------------------------------

    t1 = logical_time()

    # -----------------------------------------------------
    # Send request to master
    # -----------------------------------------------------

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:

        client_socket.settimeout(10)

        client_socket.connect((MASTER_HOST, MASTER_PORT))

        client_socket.sendall(b"TIME_REQUEST")

        # -------------------------------------------------
        # Receive master time
        # -------------------------------------------------

        data = client_socket.recv(1024)

        # -------------------------------------------------
        # T2 - Immediately after receiving response
        # -------------------------------------------------

        t2 = logical_time()

        master_time = float(data.decode())

    except Exception as e:

        print(f"\n[ERROR] Could not contact master: {e}")
        return

    finally:

        client_socket.close()

    # -----------------------------------------------------
    # Cristian's Algorithm
    # -----------------------------------------------------

    rtt = t2 - t1

    estimated_delay = rtt / 2

    synchronized_time = master_time + estimated_delay

    # Difference between synchronized client clock
    # and the master's returned time.
    synchronization_error = abs(
        synchronized_time - (master_time + estimated_delay)
    )

    # -----------------------------------------------------
    # Output
    # -----------------------------------------------------

    print("\n----- Synchronization Details -----")

    print(f"T1              : {format_time(t1)}")

    print(f"Master Time     : {format_time(master_time)}")

    print(f"T2              : {format_time(t2)}")

    print(f"RTT             : {rtt * 1000:.2f} ms")

    print(f"Estimated Delay : {estimated_delay * 1000:.2f} ms")

    print(f"Corrected Clock : {format_time(synchronized_time)}")

    print(
        f"Final Error     : "
        f"{synchronization_error * 1000:.4f} ms"
    )

    print("------------------------------------")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

print("\n" + "#" * 60)
print("        DISTRIBUTED CLOCK CLIENT")
print("#" * 60)

print(f"Client ID      : {CLIENT_ID}")
print(f"Clock Offset   : {CLOCK_OFFSET:+.1f} seconds")
print(f"Master         : {MASTER_HOST}:{MASTER_PORT}")

print("\nWaiting for master server...")

time.sleep(3)

while True:

    synchronize()

    print(f"\nNext synchronization in {SYNC_INTERVAL} seconds...")

    time.sleep(SYNC_INTERVAL)