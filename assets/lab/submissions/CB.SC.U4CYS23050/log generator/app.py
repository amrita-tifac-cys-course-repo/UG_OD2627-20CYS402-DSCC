import time
from datetime import datetime

LOG_FILE = "/app/logs/time_log.txt"

def write_log():
    while True:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"Log entry at: {current_time}\n")
        print(f"Logged time: {current_time}")
        time.sleep(5)  # logs every 5 seconds

if __name__ == "__main__":
    write_log()