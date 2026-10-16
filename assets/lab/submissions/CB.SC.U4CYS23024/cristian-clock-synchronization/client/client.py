"""Client for Cristian's clock synchronization algorithm.

    T1                = client clock just before sending TIME_REQUEST
    T2                = client clock just after receiving MASTER_TIME
    RTT               = T2 - T1
    Estimated Delay   = RTT / 2
    Synchronized Time = MASTER_TIME + RTT / 2

The client then sets its logical clock so that it read the synchronized
time at the moment T2 was taken. Only the logical clock changes; the
container's operating-system clock is never modified.
"""
import json
import os
import socket
import time

CLIENT_ID = os.getenv("CLIENT_ID", socket.gethostname())
# Initial offset of this client's clock in seconds (negative = behind)
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
MASTER_HOST = os.getenv("MASTER_HOST", "clock-master")
MASTER_PORT = int(os.getenv("MASTER_PORT", "5000"))
EXPERIMENT = os.getenv("EXPERIMENT", "default")


class LogicalClock:
    """System clock plus an adjustable offset, in seconds."""

    def __init__(self, offset: float):
        self.offset = offset

    def now(self) -> float:
        return time.time() + self.offset

    def adjust(self, correction: float) -> None:
        self.offset += correction


def fmt(ts: float) -> str:
    return time.strftime("%H:%M:%S", time.localtime(ts)) + f".{int(ts * 1000) % 1000:03d}"


def wait_for_master() -> None:
    for _ in range(30):
        try:
            socket.create_connection((MASTER_HOST, MASTER_PORT), timeout=1).close()
            return
        except OSError:
            time.sleep(1)
    raise SystemExit(f"[{CLIENT_ID}] Master {MASTER_HOST}:{MASTER_PORT} did not respond")


def main() -> None:
    wait_for_master()
    clock = LogicalClock(CLOCK_OFFSET)
    initial = clock.now()

    with socket.create_connection((MASTER_HOST, MASTER_PORT), timeout=10) as s:
        t1 = clock.now()
        s.sendall(json.dumps({"type": "TIME_REQUEST", "client_id": CLIENT_ID}).encode())
        reply = json.loads(s.recv(1024).decode())
        t2 = clock.now()

    master_time = reply["master_time"]
    rtt = t2 - t1
    delay = rtt / 2
    corrected = master_time + delay

    # Shift the logical clock so that it would have read `corrected` at T2
    clock.adjust(corrected - t2)
    # Both clocks run on the same host clock, so the offset difference is the true error
    error_ms = (clock.offset - reply["master_offset"]) * 1000

    print(f"""
========== CRISTIAN'S ALGORITHM ==========

Client ID       : {CLIENT_ID}
Experiment      : {EXPERIMENT}
Initial Clock   : {fmt(initial)}   (offset {CLOCK_OFFSET:+.3f} sec)

T1              : {fmt(t1)}
Master Time     : {fmt(master_time)}
T2              : {fmt(t2)}

RTT             : {rtt * 1000:.3f} ms
Estimated Delay : {delay * 1000:.3f} ms

Corrected Clock : {fmt(corrected)}
Final Error     : {error_ms:+.3f} ms   (accuracy bound +/- {delay * 1000:.3f} ms)

RESULT | {EXPERIMENT} | {CLIENT_ID} | {fmt(initial)} | {rtt * 1000:.3f} ms | {delay * 1000:.3f} ms | {fmt(corrected)} | {error_ms:+.3f} ms |
""", flush=True)


if __name__ == "__main__":
    main()
