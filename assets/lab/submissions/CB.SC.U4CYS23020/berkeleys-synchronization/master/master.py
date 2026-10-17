import socket
import os
import time
from datetime import datetime, timedelta

clients = {
    "Client 1": "clock-client1",
    "Client 2": "clock-client2",
    "Client 3": "clock-client3",
    "Client 4": "clock-client4"
}

PORT = 5000
BASE_DATETIME = datetime(2026, 1, 1, 12, 0, 0)

def format_clock(offset_from_base):
    dt = BASE_DATETIME + timedelta(seconds=offset_from_base)
    time_str = dt.strftime("%H:%M:%S")
    if dt.microsecond > 0:
        tenths = dt.microsecond // 100000
        if tenths > 0:
            time_str += f".{tenths}"
    return time_str

def format_offset(offset):
    if offset == int(offset):
        return f"{int(offset)}"
    return f"{offset}"

def main():
    print("========== BERKELEY ALGORITHM ==========\n")
    # Wait for clients to start
    time.sleep(5)
    
    master_offset = 0.0
    connections = {}
    client_times = {}
    
    master_time_at_poll = time.time()
    
    print("Initial Clocks\n")
    print(f"Master       : {format_clock(master_offset)}")
    
    for client_name, host in clients.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, PORT))
            connections[client_name] = sock
            
            sock.send("CLOCK_REQUEST".encode('utf-8'))
            data = sock.recv(1024).decode('utf-8')
            client_simulated_time = float(data)
            
            diff = client_simulated_time - master_time_at_poll
            diff = round(diff, 1)
            client_times[client_name] = diff
            
            print(f"{client_name.ljust(12)} : {format_clock(diff)}")
            
        except Exception as e:
            print(f"{client_name.ljust(12)} : CONNECTION FAILED ({e})")
            
    print("\n------------------------------------------\n")
    print("Clock Offsets\n")
    print(f"Master       : +0 sec")
    
    total_offset = master_offset
    valid_clients = 0
    
    outlier_threshold = 15
    enable_outlier_removal = os.environ.get("ENABLE_OUTLIER_REMOVAL", "false").lower() == "true"
    
    for client_name, offset in client_times.items():
        if enable_outlier_removal and abs(offset) > outlier_threshold:
            print(f"{client_name.ljust(12)} : {format_offset(offset)} sec (EXCLUDED - OUTLIER)")
            continue
        
        sign = "+" if offset >= 0 else ""
        print(f"{client_name.ljust(12)} : {sign}{format_offset(offset)} sec")
        total_offset += offset
        valid_clients += 1
        
    valid_nodes = valid_clients + 1
    average_offset = round(total_offset / valid_nodes, 1)
    
    sign = "+" if average_offset >= 0 else ""
    print(f"\nAverage Offset: {sign}{format_offset(average_offset)} sec\n")
    print("------------------------------------------\n")
    print("Corrections\n")
    
    master_correction = average_offset - 0
    master_offset += master_correction
    sign = "+" if master_correction >= 0 else ""
    print(f"Master       : {sign}{format_offset(round(master_correction, 1))} sec")
    
    for client_name, sock in connections.items():
        if client_name in client_times:
            client_initial_offset = client_times[client_name]
            
            if enable_outlier_removal and abs(client_initial_offset) > outlier_threshold:
                correction = 0.0
            else:
                correction = average_offset - client_initial_offset
                
            correction = round(correction, 1)
            sign = "+" if correction >= 0 else ""
            print(f"{client_name.ljust(12)} : {sign}{format_offset(correction)} sec")
            
            sock.send(f"CORRECTION:{correction}".encode('utf-8'))
            sock.recv(1024)
            sock.close()
            
    print("\n------------------------------------------\n")
    print("Final Clocks\n")
    
    print(f"Master       : {format_clock(master_offset)}")
    for client_name, offset in client_times.items():
        if enable_outlier_removal and abs(offset) > outlier_threshold:
            final_offset = offset
        else:
            final_offset = offset + (average_offset - offset)
        print(f"{client_name.ljust(12)} : {format_clock(final_offset)}")

if __name__ == "__main__":
    main()
