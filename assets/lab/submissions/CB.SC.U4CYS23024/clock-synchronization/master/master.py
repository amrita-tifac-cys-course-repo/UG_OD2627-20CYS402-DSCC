"""Master / coordinator for Berkeley's clock synchronization algorithm.

1. Polls every client with CLOCK_REQUEST.
2. Computes each node's offset relative to the master's clock,
   compensating for network delay with half the round-trip time:
       offset_i = (client_clock + RTT / 2) - master_clock_at_reply
3. Averages the offsets of the master (0) and all participating clients.
4. Correction for each node = average offset - node offset.
5. Sends each client its correction and applies its own.
6. Polls again to show the final clocks and the remaining error.

Outlier removal (OUTLIER_THRESHOLD > 0) is an implementation enhancement,
not part of the basic Berkeley algorithm: clients whose |offset| exceeds
the threshold are left out of the average but still receive a correction.
"""
import json
import os
import socket
import time

CLIENTS = [c.strip() for c in os.getenv(
    "CLIENTS", "clock-client1:5000,clock-client2:5000,clock-client3:5000,clock-client4:5000"
).split(",") if c.strip()]
# Initial offset of the master's clock in seconds
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))
# 0 disables outlier removal
OUTLIER_THRESHOLD = float(os.getenv("OUTLIER_THRESHOLD", "0"))
EXPERIMENT = os.getenv("EXPERIMENT", "default")

LINE = "-" * 50


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


def send(addr: str, msg: dict) -> dict:
    host, port = addr.rsplit(":", 1)
    with socket.create_connection((host, int(port)), timeout=5) as s:
        s.sendall(json.dumps(msg).encode())
        return json.loads(s.recv(1024).decode())


def wait_for_clients() -> None:
    for addr in CLIENTS:
        host, port = addr.rsplit(":", 1)
        for _ in range(30):
            try:
                socket.create_connection((host, int(port)), timeout=1).close()
                break
            except OSError:
                time.sleep(1)
        else:
            raise SystemExit(f"[master] Client {addr} did not respond")


def poll(clock: LogicalClock) -> list:
    """Request every client's clock and estimate its offset from the master."""
    results = []
    for addr in CLIENTS:
        t0 = clock.now()
        reply = send(addr, {"type": "CLOCK_REQUEST"})
        t1 = clock.now()
        rtt = t1 - t0
        results.append({
            "addr": addr,
            "id": reply["client_id"],
            "clock": reply["clock"],
            "rtt": rtt,
            "offset": reply["clock"] + rtt / 2 - t1,
        })
    return results


def row(name: str, value: str) -> str:
    return f"{name:<12} : {value}"


def main() -> None:
    wait_for_clients()
    clock = LogicalClock(CLOCK_OFFSET)

    print("\n========== BERKELEY ALGORITHM ==========")
    print(f"Experiment   : {EXPERIMENT}")
    print(f"Outlier rule : " + (f"exclude |offset| > {OUTLIER_THRESHOLD:g} sec"
                                if OUTLIER_THRESHOLD > 0 else "disabled (basic Berkeley)"))

    # Step 1 - poll all nodes
    master_initial = clock.now()
    clients = poll(clock)

    print("\nInitial Clocks\n")
    print(row("Master", fmt(master_initial)))
    for c in clients:
        print(row(c["id"], fmt(c["clock"])))

    # Step 2 - offsets relative to the master
    print(f"\n{LINE}\n\nClock Offsets\n")
    print(row("Master", f"{0:+.3f} sec"))
    for c in clients:
        c["included"] = OUTLIER_THRESHOLD <= 0 or abs(c["offset"]) <= OUTLIER_THRESHOLD
        note = "" if c["included"] else "   <- outlier, excluded from average"
        print(row(c["id"], f"{c['offset']:+.3f} sec  (RTT {c['rtt'] * 1000:.2f} ms){note}"))

    # Step 3 - average offset over the master and participating clients
    used = [0.0] + [c["offset"] for c in clients if c["included"]]
    avg = sum(used) / len(used)
    print(f"\nAverage Offset = ({' '.join(f'{o:+.3f}' for o in used)}) / {len(used)}")
    print(f"               = {avg:+.3f} sec")

    # Step 4 - corrections
    print(f"\n{LINE}\n\nCorrections\n")
    print(row("Master", f"{avg:+.3f} sec"))
    for c in clients:
        c["correction"] = avg - c["offset"]
        print(row(c["id"], f"{c['correction']:+.3f} sec"))

    # Step 5 - send corrections and apply our own
    for c in clients:
        send(c["addr"], {"type": "CORRECTION", "correction": c["correction"]})
    clock.adjust(avg)

    # Step 6 - final clocks and remaining error relative to the master
    master_final = clock.now()
    final = poll(clock)

    print(f"\n{LINE}\n\nFinal Clocks\n")
    print(row("Master", f"{fmt(master_final)}   (error {0:+.3f} sec)"))
    for f in final:
        print(row(f["id"], f"{fmt(f['clock'])}   (error {f['offset']:+.3f} sec)"))
    spread = max(abs(f["offset"]) for f in final)
    print(f"\nFinal synchronization error (max |offset from master|): {spread * 1000:.3f} ms")

    # Results table for the lab report (Part L)
    print(f"\n{LINE}\n\nResults Table (Markdown)\n")
    print("| Experiment | Node | Initial Clock | Offset | Average Offset | Correction | Final Clock | Error |")
    print("|---|---|---:|---:|---:|---:|---:|---:|")
    print(f"| {EXPERIMENT} | Master | {fmt(master_initial)} | +0.000 | {avg:+.3f} | {avg:+.3f} "
          f"| {fmt(master_final)} | +0.000 |")
    for c, f in zip(clients, final):
        name = c["id"] + ("" if c["included"] else " (excluded)")
        print(f"| {EXPERIMENT} | {name} | {fmt(c['clock'])} | {c['offset']:+.3f} | {avg:+.3f} "
              f"| {c['correction']:+.3f} | {fmt(f['clock'])} | {f['offset']:+.3f} |")
    print()


if __name__ == "__main__":
    main()
