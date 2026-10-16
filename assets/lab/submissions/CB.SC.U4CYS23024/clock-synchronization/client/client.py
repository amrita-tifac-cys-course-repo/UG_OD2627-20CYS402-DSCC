"""Client node for Berkeley's clock synchronization algorithm.

Keeps a logical clock that runs CLOCK_OFFSET seconds away from the
container's system clock, and answers two messages from the master
(one JSON object per TCP connection):

    {"type": "CLOCK_REQUEST"}                 -> {"client_id", "clock"}
    {"type": "CORRECTION", "correction": c}   -> applies c seconds, replies {"client_id", "clock"}
"""
import json
import os
import socket
import threading
import time

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "5000"))
CLIENT_ID = os.getenv("CLIENT_ID", socket.gethostname())
# Initial offset of this node's clock in seconds (negative = behind)
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))


class LogicalClock:
    """System clock plus an adjustable offset, in seconds."""

    def __init__(self, offset: float):
        self.offset = offset
        self.lock = threading.Lock()

    def now(self) -> float:
        with self.lock:
            return time.time() + self.offset

    def adjust(self, correction: float) -> None:
        with self.lock:
            self.offset += correction


def fmt(ts: float) -> str:
    return time.strftime("%H:%M:%S", time.localtime(ts)) + f".{int(ts * 1000) % 1000:03d}"


clock = LogicalClock(CLOCK_OFFSET)


def handle(conn: socket.socket) -> None:
    with conn:
        data = conn.recv(1024)
        if not data:
            return
        msg = json.loads(data.decode())

        if msg["type"] == "CLOCK_REQUEST":
            now = clock.now()
            print(f"[{CLIENT_ID}] CLOCK_REQUEST from master -> sending {fmt(now)}", flush=True)
            reply = {"client_id": CLIENT_ID, "clock": now}

        elif msg["type"] == "CORRECTION":
            correction = float(msg["correction"])
            before = clock.now()
            clock.adjust(correction)
            after = clock.now()
            print(f"[{CLIENT_ID}] CORRECTION {correction:+.3f} sec received", flush=True)
            print(f"[{CLIENT_ID}]   Clock before: {fmt(before)}", flush=True)
            print(f"[{CLIENT_ID}]   Clock after : {fmt(after)}", flush=True)
            reply = {"client_id": CLIENT_ID, "clock": after}

        else:
            reply = {"error": f"unknown message type {msg['type']}"}

        conn.sendall(json.dumps(reply).encode())


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[{CLIENT_ID}] Listening on port {PORT}, initial offset {CLOCK_OFFSET:+.3f} sec, "
              f"clock {fmt(clock.now())}", flush=True)
        while True:
            conn, _ = s.accept()
            threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
