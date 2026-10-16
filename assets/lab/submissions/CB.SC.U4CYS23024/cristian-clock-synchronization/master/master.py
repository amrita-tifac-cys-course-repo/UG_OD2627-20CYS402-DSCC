"""Master / time server for Cristian's clock synchronization algorithm.

Listens on TCP and answers every TIME_REQUEST with its logical clock.
An optional artificial delay (ARTIFICIAL_DELAY_MS) simulates network
latency, applied according to DELAY_MODE:

    symmetric  half before reading the clock, half after (request = reply delay)
    request    all of it before reading the clock (slow request path)
    response   all of it after reading the clock (slow reply path)
"""
import json
import os
import socket
import threading
import time

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "5000"))
# Offset of the master's logical clock in seconds
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
ARTIFICIAL_DELAY_MS = float(os.getenv("ARTIFICIAL_DELAY_MS", "0"))
DELAY_MODE = os.getenv("DELAY_MODE", "symmetric")

if DELAY_MODE == "request":
    BEFORE, AFTER = ARTIFICIAL_DELAY_MS, 0.0
elif DELAY_MODE == "response":
    BEFORE, AFTER = 0.0, ARTIFICIAL_DELAY_MS
else:
    BEFORE = AFTER = ARTIFICIAL_DELAY_MS / 2


class LogicalClock:
    """System clock plus a fixed offset, in seconds."""

    def __init__(self, offset: float):
        self.offset = offset

    def now(self) -> float:
        return time.time() + self.offset


def fmt(ts: float) -> str:
    return time.strftime("%H:%M:%S", time.localtime(ts)) + f".{int(ts * 1000) % 1000:03d}"


clock = LogicalClock(CLOCK_OFFSET)


def handle(conn: socket.socket) -> None:
    with conn:
        msg = json.loads(conn.recv(1024).decode())
        if msg.get("type") != "TIME_REQUEST":
            conn.sendall(json.dumps({"error": "expected TIME_REQUEST"}).encode())
            return
        time.sleep(BEFORE / 1000)
        master_time = clock.now()
        time.sleep(AFTER / 1000)
        # master_offset is only used by the client to report its final error
        reply = {"master_time": master_time, "master_offset": CLOCK_OFFSET}
        conn.sendall(json.dumps(reply).encode())
        print(f"[master] TIME_REQUEST from {msg.get('client_id', '?')} -> "
              f"MASTER_TIME = {fmt(master_time)}", flush=True)


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[master] Time server listening on port {PORT}", flush=True)
        print(f"[master] Clock offset {CLOCK_OFFSET:+.3f} sec, clock {fmt(clock.now())}", flush=True)
        print(f"[master] Artificial delay {ARTIFICIAL_DELAY_MS:g} ms ({DELAY_MODE}: "
              f"{BEFORE:g} ms before reading the clock, {AFTER:g} ms after)", flush=True)
        while True:
            conn, _ = s.accept()
            threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
