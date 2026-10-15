import socket
import time
import os
import datetime
import sys

MASTER_HOST = os.getenv('MASTER_HOST', 'master')
MASTER_PORT = 5000
CLIENT_ID = os.getenv('CLIENT_ID', 'Unknown')
CLOCK_OFFSET = float(os.getenv('CLOCK_OFFSET', '0.0'))

def get_logical_time():
    return time.time() + CLOCK_OFFSET

def format_time(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S.%f')[:-3]

def run_client():
    print(f"Starting {CLIENT_ID} with initial offset: {CLOCK_OFFSET}s")
    time.sleep(3)  # Wait for master to fully start

    # Stagger client starts so they sync one-by-one
    client_number = int(CLIENT_ID.split("-")[1])   # "Client-2" -> 2 (uppercase CLIENT_ID!)
    time.sleep((client_number - 1) * 2)            # 0s, 2s, 4s, 6s

    initial_clock = get_logical_time()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((MASTER_HOST, MASTER_PORT))

            # Step 1: Record T1 (client logical time before request)
            T1_logical = get_logical_time()
            T1_real = time.time()   # real time for accurate RTT measurement

            # Step 2: Send request
            s.sendall(b"TIME_REQUEST")

            # Step 3: Receive master time
            data = s.recv(1024).decode()
            master_time = float(data)

            # Step 4: Record T2 (client logical time after response)
            T2_real = time.time()
            T2_logical = get_logical_time()

            # Step 5: Calculate RTT (real time avoids offset skew)
            RTT = T2_real - T1_real

            # Step 6: Estimate one-way network delay
            delay = RTT / 2

            # Step 7: Calculate synchronized time (Cristian's formula)
            corrected_clock = master_time + delay

            # Error bound = maximum possible error (network asymmetry)
            error_bound_ms = delay * 1000

            print("\n========== CRISTIAN'S ALGORITHM ==========")
            print(f"Client ID       : {CLIENT_ID}")
            print(f"Initial Clock   : {format_time(initial_clock)}")
            print(f"T1              : {format_time(T1_logical)}")
            print(f"Master Time     : {format_time(master_time)}")
            print(f"T2              : {format_time(T2_logical)}")
            print(f"RTT             : {RTT*1000:.0f} ms")
            print(f"Estimated Delay : {delay*1000:.0f} ms")
            print(f"Corrected Clock : {format_time(corrected_clock)}")
            print(f"Final Error     : 0 ms (Ideal) / ±{error_bound_ms:.0f} ms (Bound)")
            print("==========================================\n")

    except Exception as e:
        print(f"Error connecting to master: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_client()
