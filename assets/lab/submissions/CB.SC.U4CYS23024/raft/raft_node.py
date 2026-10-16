"""A Raft node: leader election + log replication over HTTP/JSON.

Each node keeps a replicated key-value store. Clients send commands
("SET key value" / "DEL key") to the leader; the leader appends them to
its log, replicates them to followers, and applies them once a majority
has stored them (committed).

Endpoints
  GET  /status          node state, term, leader, log and data
  POST /submit          {"command": "SET x 5"}   (leader only)
  POST /request_vote    Raft RequestVote RPC
  POST /append_entries  Raft AppendEntries RPC (also the heartbeat)
"""
import json
import os
import random
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

NODE_ID = os.getenv("NODE_ID", "node1")
PORT = int(os.getenv("PORT", "8000"))
PEERS = [p.strip() for p in os.getenv("PEERS", "").split(",") if p.strip()]  # host:port
ELECTION_MIN = float(os.getenv("ELECTION_MIN_MS", "1500")) / 1000
ELECTION_MAX = float(os.getenv("ELECTION_MAX_MS", "3000")) / 1000
HEARTBEAT = float(os.getenv("HEARTBEAT_MS", "500")) / 1000
RPC_TIMEOUT = float(os.getenv("RPC_TIMEOUT_MS", "400")) / 1000
MAJORITY = (len(PEERS) + 1) // 2 + 1


def log(msg: str) -> None:
    print(f"{time.strftime('%H:%M:%S')} [{NODE_ID}] {msg}", flush=True)


def rpc(peer: str, path: str, payload: dict):
    req = urllib.request.Request(
        f"http://{peer}/{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=RPC_TIMEOUT) as r:
            return json.loads(r.read())
    except Exception:
        return None  # peer down, paused or slow: treat as no reply


class RaftNode:
    def __init__(self):
        self.lock = threading.RLock()
        self.committed = threading.Condition(self.lock)
        # Persistent state (kept in memory for this demo)
        self.term = 0
        self.voted_for = None
        self.log = [{"term": 0, "command": None}]  # index 0 is a sentinel; real entries start at 1
        # Volatile state
        self.state = "follower"
        self.leader_id = None
        self.commit_index = 0
        self.last_applied = 0
        self.data = {}
        # Leader-only state
        self.next_index = {}
        self.match_index = {}
        self.last_heartbeat = 0.0
        self.reset_election_timer()

    # ---------- helpers (call with lock held) ----------
    def reset_election_timer(self):
        self.election_deadline = time.time() + random.uniform(ELECTION_MIN, ELECTION_MAX)

    def last_log(self):
        return len(self.log) - 1, self.log[-1]["term"]

    def become_follower(self, term, leader=None):
        if term > self.term:
            self.term = term
            self.voted_for = None
        if self.state != "follower":
            log(f"Stepping down to FOLLOWER (term {self.term})")
        self.state = "follower"
        if leader and leader != self.leader_id:
            log(f"Following leader {leader} (term {self.term})")
        self.leader_id = leader
        self.reset_election_timer()

    def become_leader(self):
        self.state = "leader"
        self.leader_id = NODE_ID
        last_idx, _ = self.last_log()
        self.next_index = {p: last_idx + 1 for p in PEERS}
        self.match_index = {p: 0 for p in PEERS}
        self.last_heartbeat = 0.0  # send heartbeats immediately
        log(f"*** Became LEADER for term {self.term} ***")

    def apply_committed(self):
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            cmd = self.log[self.last_applied]["command"]
            parts = cmd.split()
            if parts[0].upper() == "SET" and len(parts) >= 3:
                self.data[parts[1]] = " ".join(parts[2:])
            elif parts[0].upper() == "DEL" and len(parts) == 2:
                self.data.pop(parts[1], None)
            log(f"Applied #{self.last_applied}: {cmd}  -> data={self.data}")
        self.committed.notify_all()

    def advance_commit(self):
        """Leader: commit the highest index stored on a majority (current term only)."""
        for n in range(len(self.log) - 1, self.commit_index, -1):
            if self.log[n]["term"] < self.term:
                break  # Raft only commits entries from the current term by counting
            replicas = 1 + sum(1 for p in PEERS if self.match_index[p] >= n)
            if replicas >= MAJORITY:
                log(f"Entry #{n} stored on {replicas}/{len(PEERS) + 1} nodes -> COMMITTED")
                self.commit_index = n
                self.apply_committed()
                break

    # ---------- election ----------
    def start_election(self):
        with self.lock:
            self.state = "candidate"
            self.term += 1
            self.voted_for = NODE_ID
            self.leader_id = None
            self.reset_election_timer()
            term = self.term
            last_idx, last_term = self.last_log()
            votes = [1]
        log(f"Election timeout -> CANDIDATE for term {term}, requesting votes")
        args = {"term": term, "candidate_id": NODE_ID,
                "last_log_index": last_idx, "last_log_term": last_term}

        def ask(peer):
            resp = rpc(peer, "request_vote", args)
            if not resp:
                return
            with self.lock:
                if resp["term"] > self.term:
                    self.become_follower(resp["term"])
                    return
                if self.state != "candidate" or self.term != term:
                    return
                if resp["vote_granted"]:
                    votes[0] += 1
                    log(f"Vote from {peer} ({votes[0]}/{MAJORITY} needed)")
                    if votes[0] >= MAJORITY:
                        self.become_leader()

        if votes[0] >= MAJORITY:  # single-node cluster
            with self.lock:
                self.become_leader()
        for p in PEERS:
            threading.Thread(target=ask, args=(p,), daemon=True).start()

    def on_request_vote(self, a):
        with self.lock:
            if a["term"] > self.term:
                self.become_follower(a["term"])
            granted = False
            if a["term"] == self.term and self.voted_for in (None, a["candidate_id"]):
                my_idx, my_term = self.last_log()
                up_to_date = (a["last_log_term"] > my_term or
                              (a["last_log_term"] == my_term and a["last_log_index"] >= my_idx))
                if up_to_date:
                    self.voted_for = a["candidate_id"]
                    self.reset_election_timer()
                    granted = True
                    log(f"Voted for {a['candidate_id']} in term {self.term}")
            return {"term": self.term, "vote_granted": granted}

    # ---------- replication ----------
    def send_append(self, peer):
        with self.lock:
            if self.state != "leader":
                return
            term = self.term
            prev_idx = self.next_index[peer] - 1
            entries = self.log[prev_idx + 1:]
            args = {"term": term, "leader_id": NODE_ID,
                    "prev_log_index": prev_idx, "prev_log_term": self.log[prev_idx]["term"],
                    "entries": entries, "leader_commit": self.commit_index}
        resp = rpc(peer, "append_entries", args)
        if not resp:
            return
        with self.lock:
            if resp["term"] > self.term:
                self.become_follower(resp["term"])
                return
            if self.state != "leader" or self.term != term:
                return
            if resp["success"]:
                self.match_index[peer] = max(self.match_index[peer], prev_idx + len(entries))
                self.next_index[peer] = self.match_index[peer] + 1
                self.advance_commit()
            else:
                # Logs disagree: back up and retry on the next heartbeat
                self.next_index[peer] = max(1, self.next_index[peer] - 1)

    def broadcast_append(self):
        for p in PEERS:
            threading.Thread(target=self.send_append, args=(p,), daemon=True).start()

    def on_append_entries(self, a):
        with self.lock:
            if a["term"] < self.term:
                return {"term": self.term, "success": False}  # stale leader
            self.become_follower(a["term"], leader=a["leader_id"])
            pi = a["prev_log_index"]
            if pi >= len(self.log) or self.log[pi]["term"] != a["prev_log_term"]:
                return {"term": self.term, "success": False}  # consistency check failed
            idx, added = pi + 1, 0
            for e in a["entries"]:
                if idx < len(self.log) and self.log[idx]["term"] != e["term"]:
                    del self.log[idx:]  # remove conflicting entries
                if idx >= len(self.log):
                    self.log.append(e)
                    added += 1
                idx += 1
            if added:
                log(f"Appended {added} entr{'y' if added == 1 else 'ies'} from {a['leader_id']} "
                    f"(log length {len(self.log) - 1})")
            if a["leader_commit"] > self.commit_index:
                self.commit_index = min(a["leader_commit"], len(self.log) - 1)
                self.apply_committed()
            return {"term": self.term, "success": True}

    # ---------- client requests ----------
    def submit(self, command):
        command = (command or "").strip()
        parts = command.split()
        if not parts or parts[0].upper() not in ("SET", "DEL"):
            return {"ok": False, "error": "command must be 'SET key value' or 'DEL key'"}
        with self.lock:
            if self.state != "leader":
                return {"ok": False, "error": "not the leader", "leader": self.leader_id}
            self.log.append({"term": self.term, "command": command})
            index, term = len(self.log) - 1, self.term
            log(f"Client command '{command}' -> log entry #{index}")
        self.broadcast_append()
        deadline = time.time() + 3
        with self.committed:
            while self.commit_index < index and self.state == "leader" and time.time() < deadline:
                self.committed.wait(0.1)
            ok = self.commit_index >= index and self.log[index]["term"] == term
            return {"ok": ok, "index": index, "term": term, "data": dict(self.data),
                    **({} if ok else {"error": "not committed (no majority reachable?)"})}

    def status(self):
        with self.lock:
            return {"id": NODE_ID, "state": self.state, "term": self.term,
                    "leader": self.leader_id, "voted_for": self.voted_for,
                    "log": [{"index": i, **e} for i, e in enumerate(self.log) if i > 0],
                    "commit_index": self.commit_index, "data": dict(self.data)}

    # ---------- main loop ----------
    def run(self):
        while True:
            time.sleep(0.05)
            with self.lock:
                now = time.time()
                if self.state == "leader":
                    action = "heartbeat" if now - self.last_heartbeat >= HEARTBEAT else None
                    if action:
                        self.last_heartbeat = now
                else:
                    action = "election" if now >= self.election_deadline else None
            if action == "heartbeat":
                self.broadcast_append()
            elif action == "election":
                self.start_election()


node = RaftNode()


class Handler(BaseHTTPRequestHandler):
    def _send(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/status":
            self._send(node.status())
        else:
            self._send({"error": "not found"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._send({"error": "bad json"}, 400)
        routes = {"/request_vote": node.on_request_vote,
                  "/append_entries": node.on_append_entries,
                  "/submit": lambda b: node.submit(b.get("command"))}
        if self.path in routes:
            self._send(routes[self.path](body))
        else:
            self._send({"error": "not found"}, 404)

    def log_message(self, *args):
        pass  # keep the console for Raft events only


if __name__ == "__main__":
    log(f"Starting on port {PORT} with peers {PEERS} (majority = {MAJORITY})")
    threading.Thread(target=node.run, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
