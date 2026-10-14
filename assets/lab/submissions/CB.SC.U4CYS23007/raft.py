import threading
import random
import time
import heapq
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, List

# Data types

class State(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


@dataclass
class LogEntry:
    term: int
    command: Any           


# RPC message bodies 

@dataclass
class RequestVote:
    term: int
    candidate_id: int
    last_log_index: int
    last_log_term: int


@dataclass
class RequestVoteReply:
    term: int
    vote_granted: bool


@dataclass
class AppendEntries:
    term: int
    leader_id: int
    prev_log_index: int
    prev_log_term: int
    entries: List[LogEntry]
    leader_commit: int


@dataclass
class AppendEntriesReply:
    term: int
    success: bool
    match_index: int       

# Simulated network: delays, drops, and partitions

class Network:
    """In-memory message router with a single delivery scheduler thread."""

    def __init__(self):
        self.nodes = {}
        self.drop_rate = 0.0        # fraction of messages randomly dropped
        self.isolated = set()       # node ids currently partitioned off
        self._heap = []             # (deliver_at, seq, src, dst, msg)
        self._seq = 0
        self._cv = threading.Condition()
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def register(self, node):
        self.nodes[node.id] = node

    def send(self, src, dst, msg):
        if random.random() < self.drop_rate:
            return
        with self._cv:
            if src in self.isolated or dst in self.isolated:
                return  # can't cross a partition boundary
            deliver_at = time.time() + random.uniform(0.005, 0.03)
            heapq.heappush(self._heap, (deliver_at, self._seq, src, dst, msg))
            self._seq += 1
            self._cv.notify()

    def _loop(self):
        while self.running:
            with self._cv:
                if not self._heap:
                    self._cv.wait(timeout=0.1)
                    continue
                deliver_at, _seq, src, dst, msg = self._heap[0]
                now = time.time()
                if deliver_at > now:
                    self._cv.wait(timeout=deliver_at - now)
                    continue
                heapq.heappop(self._heap)
            node = self.nodes.get(dst)
            if node and dst not in self.isolated:
                node.inbox.put((src, msg))

    def stop(self):
        self.running = False
        with self._cv:
            self._cv.notify()


# Raft node

# Timescale chosen so a human can watch the demo. Real Raft uses ~10-50ms
# heartbeats and ~150-300ms election timeouts.
HEARTBEAT_INTERVAL = 0.10
ELECTION_TIMEOUT = (0.30, 0.60)


class RaftNode:
    def __init__(self, node_id: int, all_ids: List[int], net: Network):
        self.id = node_id
        self.all_ids = list(all_ids)
        self.peers = [i for i in all_ids if i != node_id]
        self.net = net
        net.register(self)

        # Persistent state (would be written to stable storage before replying)
        self.current_term = 0
        self.voted_for: Optional[int] = None
        self.log: List[LogEntry] = [LogEntry(term=0, command=None)]  # index-0 sentinel

        # Volatile state (all servers)
        self.commit_index = 0
        self.last_applied = 0
        self.state = State.FOLLOWER
        self.leader_id: Optional[int] = None

        # Volatile state (leaders only)
        self.next_index = {}
        self.match_index = {}

        # Election bookkeeping
        self.votes_received = set()
        self.election_deadline = 0.0
        self.last_heartbeat = 0.0

        # Application: replicated key-value store
        self.kv = {}

        self.inbox = __import__("queue").Queue()
        self.lock = threading.RLock()
        self.running = False
        self._thread = None

    # lifecycle

    def start(self):
        self.running = True
        self._reset_election_timer()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            now = time.time()
            with self.lock:
                if self.state == State.LEADER:
                    if now - self.last_heartbeat >= HEARTBEAT_INTERVAL:
                        self._broadcast_append_entries()
                        self.last_heartbeat = now
                elif now >= self.election_deadline:
                    self._start_election()
            try:
                src, body = self.inbox.get(timeout=0.01)
            except Exception:
                continue
            self._handle_message(src, body)

    # timers 

    def _reset_election_timer(self):
        self.election_deadline = time.time() + random.uniform(*ELECTION_TIMEOUT)

    # role transitions

    def _step_down(self, term: int):
        """Discover a higher term -> revert to follower."""
        self.current_term = term
        self.state = State.FOLLOWER
        self.voted_for = None
        self._reset_election_timer()

    def _start_election(self):
        self.state = State.CANDIDATE
        self.current_term += 1
        self.voted_for = self.id
        self.votes_received = {self.id}
        self._reset_election_timer()

        last_index = len(self.log) - 1
        last_term = self.log[last_index].term
        for peer in self.peers:
            self.net.send(self.id, peer, RequestVote(
                term=self.current_term,
                candidate_id=self.id,
                last_log_index=last_index,
                last_log_term=last_term,
            ))

    def _become_leader(self):
        self.state = State.LEADER
        self.leader_id = self.id
        last_index = len(self.log) - 1
        self.next_index = {p: last_index + 1 for p in self.peers}
        self.match_index = {p: 0 for p in self.peers}
        self.last_heartbeat = 0.0  # force an immediate heartbeat
        print(f"[node {self.id}] became LEADER for term {self.current_term}")

    # message dispatch 

    def _handle_message(self, src, body):
        with self.lock:
            if isinstance(body, RequestVote):
                self._on_request_vote(src, body)
            elif isinstance(body, RequestVoteReply):
                self._on_request_vote_reply(src, body)
            elif isinstance(body, AppendEntries):
                self._on_append_entries(src, body)
            elif isinstance(body, AppendEntriesReply):
                self._on_append_entries_reply(src, body)

    # RequestVote 

    def _on_request_vote(self, src, rv: RequestVote):
        if rv.term > self.current_term:
            self._step_down(rv.term)

        granted = False
        if rv.term == self.current_term:
            my_last_index = len(self.log) - 1
            my_last_term = self.log[my_last_index].term
            # candidate log must be at least as up-to-date as ours
            log_ok = (rv.last_log_term > my_last_term or
                      (rv.last_log_term == my_last_term and
                       rv.last_log_index >= my_last_index))
            if self.voted_for in (None, rv.candidate_id) and log_ok:
                self.voted_for = rv.candidate_id
                granted = True
                self._reset_election_timer()

        self.net.send(self.id, src,
                      RequestVoteReply(term=self.current_term, vote_granted=granted))

    def _on_request_vote_reply(self, src, reply: RequestVoteReply):
        if reply.term > self.current_term:
            self._step_down(reply.term)
            return
        if self.state != State.CANDIDATE or reply.term != self.current_term:
            return
        if reply.vote_granted:
            self.votes_received.add(src)
            if len(self.votes_received) > len(self.all_ids) // 2:
                self._become_leader()

    # AppendEntries

    def _on_append_entries(self, src, ae: AppendEntries):
        if ae.term > self.current_term:
            self._step_down(ae.term)

        success = False
        match_index = 0
        if ae.term == self.current_term:
            self.state = State.FOLLOWER
            self.leader_id = ae.leader_id
            self._reset_election_timer()

            # Log consistency check: do we have prev_log_index with matching term?
            if (ae.prev_log_index < len(self.log) and
                    self.log[ae.prev_log_index].term == ae.prev_log_term):
                success = True
                # Splice in the new entries, truncating on first conflict.
                for i, entry in enumerate(ae.entries):
                    index = ae.prev_log_index + 1 + i
                    if index < len(self.log):
                        if self.log[index].term != entry.term:
                            self.log = self.log[:index]
                            self.log.append(entry)
                    else:
                        self.log.append(entry)
                match_index = ae.prev_log_index + len(ae.entries)

                # Advance commit index and apply.
                if ae.leader_commit > self.commit_index:
                    self.commit_index = min(ae.leader_commit, len(self.log) - 1)
                    self._apply_committed()

        self.net.send(self.id, src, AppendEntriesReply(
            term=self.current_term, success=success, match_index=match_index))

    def _on_append_entries_reply(self, src, reply: AppendEntriesReply):
        if reply.term > self.current_term:
            self._step_down(reply.term)
            return
        if self.state != State.LEADER or reply.term != self.current_term:
            return

        if reply.success:
            self.match_index[src] = max(self.match_index[src], reply.match_index)
            self.next_index[src] = self.match_index[src] + 1
            self._advance_commit_index()
        else:
            # Follower rejected: back off and retry immediately.
            self.next_index[src] = max(1, self.next_index[src] - 1)
            self._send_append_entries(src)

    # replication helpers (leader) 

    def _send_append_entries(self, peer):
        ni = self.next_index[peer]
        prev_index = ni - 1
        prev_term = self.log[prev_index].term
        entries = self.log[ni:]
        self.net.send(self.id, peer, AppendEntries(
            term=self.current_term,
            leader_id=self.id,
            prev_log_index=prev_index,
            prev_log_term=prev_term,
            entries=entries,
            leader_commit=self.commit_index,
        ))

    def _broadcast_append_entries(self):
        for peer in self.peers:
            self._send_append_entries(peer)

    def _advance_commit_index(self):
        """Find the highest N replicated on a majority whose term is current."""
        last_index = len(self.log) - 1
        for n in range(last_index, self.commit_index, -1):
            if self.log[n].term != self.current_term:
                continue  # Raft only commits current-term entries directly
            count = 1  # the leader itself
            for p in self.peers:
                if self.match_index[p] >= n:
                    count += 1
            if count > len(self.all_ids) // 2:
                self.commit_index = n
                self._apply_committed()
                break

    # state machine 

    def _apply_committed(self):
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            cmd = self.log[self.last_applied].command
            self._apply(cmd)

    def _apply(self, command):
        if command is None:
            return
        op = command[0]
        if op == "set":
            _, key, value = command
            self.kv[key] = value

    # client interface

    def submit(self, command):
        """Client entry point. Returns (accepted, leader_hint)."""
        with self.lock:
            if self.state != State.LEADER:
                return False, self.leader_id
            self.log.append(LogEntry(term=self.current_term, command=command))
            self._broadcast_append_entries()
            return True, self.id


# Demo 

def find_leader(nodes):
    leaders = [n for n in nodes if n.state == State.LEADER]
    # Prefer the leader with the highest term if there's transient overlap.
    return max(leaders, key=lambda n: n.current_term) if leaders else None


def wait_for_leader(nodes, timeout=5.0):
    start = time.time()
    while time.time() - start < timeout:
        leader = find_leader(nodes)
        if leader:
            return leader
        time.sleep(0.05)
    return None


def submit_and_wait(nodes, command, timeout=3.0):
    start = time.time()
    while time.time() - start < timeout:
        leader = find_leader(nodes)
        if leader:
            ok, hint = leader.submit(command)
            if ok:
                return leader
        time.sleep(0.05)
    return None


def main():
    random.seed(42)
    net = Network()
    ids = [0, 1, 2, 3, 4]
    nodes = [RaftNode(i, ids, net) for i in ids]
    for n in nodes:
        n.start()

    print("=== Booting 5-node cluster, waiting for a leader ===")
    leader = wait_for_leader(nodes)
    print(f"Leader elected: node {leader.id} (term {leader.current_term})\n")

    print("=== Replicating 3 commands ===")
    for cmd in [("set", "x", 1), ("set", "y", 2), ("set", "x", 9)]:
        submit_and_wait(nodes, cmd)
        print(f"submitted {cmd}")
    time.sleep(0.5)

    print("\n=== Partitioning the current leader to force re-election ===")
    old_leader = find_leader(nodes)
    with net._cv:
        net.isolated.add(old_leader.id)
    print(f"node {old_leader.id} isolated")

    new_leader = None
    start = time.time()
    while time.time() - start < 5.0:
        cand = find_leader([n for n in nodes if n.id != old_leader.id])
        if cand and cand.id != old_leader.id:
            new_leader = cand
            break
        time.sleep(0.05)
    print(f"New leader elected: node {new_leader.id} (term {new_leader.current_term})")

    print("\n=== Committing a command under the new leader ===")
    submit_and_wait([n for n in nodes if n.id != old_leader.id], ("set", "z", 42))
    time.sleep(0.5)

    print("\n=== Healing the partition ===")
    with net._cv:
        net.isolated.discard(old_leader.id)
    time.sleep(1.0)  # let the old leader catch up as a follower

    print("\n=== Final cluster state ===")
    for n in sorted(nodes, key=lambda x: x.id):
        log_terms = [e.term for e in n.log]
        print(f"node {n.id}: state={n.state.value:9s} term={n.current_term} "
              f"commit={n.commit_index} kv={n.kv} log_terms={log_terms}")

    # Consistency check: every committed prefix should match across nodes.
    min_commit = min(n.commit_index for n in nodes if n.id not in net.isolated)
    ref = nodes[0].log
    consistent = all(
        [e.term for e in n.log[:min_commit + 1]] == [e.term for e in ref[:min_commit + 1]]
        for n in nodes
    )
    print(f"\nCommitted logs consistent across nodes: {consistent}")

    for n in nodes:
        n.stop()
    net.stop()


if __name__ == "__main__":
    main()
