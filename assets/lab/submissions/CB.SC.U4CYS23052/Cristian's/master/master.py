import socket
import time
import os
import datetime

HOST = '0.0.0.0'
PORT = 5000
# Read artificial delay from environment variable (default 0.0)
ARTIFICIAL_DELAY = float(os.getenv('MASTER_DELAY', '0.0'))

def get_master_time():
    return time.time()

def format_time(ts):
    return datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S.%f')[:-3]

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Master Time Server started on port {PORT} | Artificial Delay: {ARTIFICIAL_DELAY}s")
        
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode()
                if data == "TIME_REQUEST":
                    # Introduce artificial processing delay BEFORE taking the timestamp
                    if ARTIFICIAL_DELAY > 0:
                        time.sleep(ARTIFICIAL_DELAY)
                        
                    current_time = get_master_time()
                    conn.sendall(str(current_time).encode())
                    print(f"Request from {addr[0]} -> Sent time: {format_time(current_time)}")

if __name__ == '__main__':
    start_server()
