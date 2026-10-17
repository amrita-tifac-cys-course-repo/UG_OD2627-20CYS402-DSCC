import socket
import os
import time
from datetime import datetime, timedelta

CLIENT_ID = os.environ.get("CLIENT_ID", "Client")
CLOCK_OFFSET = float(os.environ.get("CLOCK_OFFSET", "0"))
MASTER_HOST = "clock-master"
PORT = 5000

def format_t(t):
    dt = datetime.fromtimestamp(t)
    return dt.strftime("%H:%M:%S.%f")[:-3]

def main():
    time.sleep(3) # wait for master
    
    t1_real = time.time()
    t1_logical = t1_real + CLOCK_OFFSET
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((MASTER_HOST, PORT))
        sock.send("TIME_REQUEST".encode('utf-8'))
        
        data = sock.recv(1024).decode('utf-8')
        master_time = float(data)
        
        t2_real = time.time()
        t2_logical = t2_real + CLOCK_OFFSET
        sock.close()
        
        rtt_seconds = t2_real - t1_real
        delay_seconds = rtt_seconds / 2
        
        sync_time = master_time + delay_seconds
        
        # In this deterministic local environment, master's true time is exactly t2_real.
        # So error is abs(sync_time - t2_real)
        error_ms = abs(sync_time - t2_real) * 1000
        
        print(f"========== CRISTIAN'S ALGORITHM ==========\n")
        print(f"Client ID       : {CLIENT_ID}")
        print(f"Initial Clock   : {format_t(t1_logical)}\n")
        print(f"T1              : {format_t(t1_logical)}")
        print(f"Master Time     : {format_t(master_time)}")
        print(f"T2              : {format_t(t2_logical)}\n")
        print(f"RTT             : {rtt_seconds * 1000:.1f} ms")
        print(f"Estimated Delay : {delay_seconds * 1000:.1f} ms\n")
        print(f"Corrected Clock : {format_t(sync_time)}")
        print(f"Final Error     : {error_ms:.1f} ms\n")
        
    except Exception as e:
        print(f"Failed to connect to master: {e}")

if __name__ == "__main__":
    main()
