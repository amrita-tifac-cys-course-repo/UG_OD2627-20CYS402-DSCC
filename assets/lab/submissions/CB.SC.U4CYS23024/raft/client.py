"""Command-line client for the Raft cluster.

  python client.py status          show every node's state
  python client.py watch           refresh the status table every second
  python client.py set <key> <v>   write a value (sent to the current leader)
  python client.py del <key>       delete a key
"""
import json
import os
import sys
import time
import urllib.request

NODES = [n.strip() for n in os.getenv(
    "NODES", "node1:8000,node2:8000,node3:8000,node4:8000,node5:8000").split(",") if n.strip()]


def get(addr):
    try:
        with urllib.request.urlopen(f"http://{addr}/status", timeout=1) as r:
            return json.loads(r.read())
    except Exception:
        return None


def post(addr, payload):
    req = urllib.request.Request(f"http://{addr}/submit", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())


def status_table():
    rows = [f"{'NODE':<12}{'STATE':<11}{'TERM':>5}  {'LEADER':<8}{'LOG':>4}{'COMMIT':>7}  DATA"]
    for addr in NODES:
        s = get(addr)
        if s is None:
            rows.append(f"{addr.split(':')[0]:<12}DOWN")
            continue
        state = s["state"].upper() + (" *" if s["state"] == "leader" else "")
        rows.append(f"{s['id']:<12}{state:<11}{s['term']:>5}  {str(s['leader']):<8}"
                    f"{len(s['log']):>4}{s['commit_index']:>7}  {s['data']}")
    return "\n".join(rows)


def find_leader():
    leaders = []
    for addr in NODES:
        s = get(addr)
        if s and s["state"] == "leader":
            leaders.append((s["term"], addr))
    return max(leaders)[1] if leaders else None


def submit(command):
    for _ in range(10):
        leader = find_leader()
        if leader:
            print(f"Sending '{command}' to leader {leader}")
            resp = post(leader, {"command": command})
            print(json.dumps(resp, indent=2))
            return
        print("No leader right now (election in progress?), retrying...")
        time.sleep(1)
    print("Gave up: no leader found. Is a majority of nodes running?")


def main():
    args = sys.argv[1:]
    if not args or args[0] == "status":
        print(status_table())
    elif args[0] == "watch":
        try:
            while True:
                print("\033[2J\033[H" + time.strftime("%H:%M:%S") + "  (Ctrl+C to stop)\n")
                print(status_table())
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    elif args[0] == "set" and len(args) >= 3:
        submit(f"SET {args[1]} {' '.join(args[2:])}")
    elif args[0] == "del" and len(args) == 2:
        submit(f"DEL {args[1]}")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
