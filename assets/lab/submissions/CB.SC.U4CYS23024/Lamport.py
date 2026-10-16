"""
Lab #7A - Lamport Logical Clock
20CYS402 - Distributed Systems and Cloud Computing

Simulates 3 distributed processes (P1, P2, P3), each with its own logical
clock. Supports LOCAL, SEND and RECEIVE events, computes Lamport timestamps
dynamically, and demonstrates causal ordering and concurrent events.
"""

from collections import deque
from dataclasses import dataclass
from itertools import combinations


# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
@dataclass
class Message:
    msg_id: str
    sender: str
    receiver: str
    timestamp: int          # Lamport timestamp attached by the sender

    def __str__(self):
        return (f"Message ID        : {self.msg_id}\n"
                f"Sender            : {self.sender}\n"
                f"Receiver          : {self.receiver}\n"
                f"Lamport Timestamp : {self.timestamp}")


@dataclass
class Event:
    event_id: str
    process: str
    etype: str              # LOCAL / SEND / RECEIVE
    timestamp: int
    msg_id: str = ""        # set for SEND / RECEIVE


class Process:
    """A simulated distributed process with its own logical clock."""

    def __init__(self, name):
        self.name = name
        self.clock = 0          # independent logical clock, starts at 0
        self.inbox = deque()    # delivered-but-not-yet-received messages
        self.history = []       # events of this process in program order


# ----------------------------------------------------------------------
# Distributed system simulator
# ----------------------------------------------------------------------
class DistributedSystem:
    def __init__(self, process_names):
        self.processes = {n: Process(n) for n in process_names}
        self.log = []           # global log in execution order
        self.event_count = 0
        self.msg_count = 0

    def _record(self, proc, etype, msg_id=""):
        self.event_count += 1
        ev = Event(f"E{self.event_count}", proc.name, etype, proc.clock, msg_id)
        proc.history.append(ev)
        self.log.append(ev)
        extra = f" ({msg_id})" if msg_id else ""
        print(f"  {ev.event_id:<4} {proc.name}: {etype:<8}{extra:<6} -> C{proc.name[1:]} = {proc.clock}")
        return ev

    # Rule 1: local event  ->  C = C + 1
    def local_event(self, pname):
        p = self.processes[pname]
        p.clock += 1
        return self._record(p, "LOCAL")

    # Rule 2: send  ->  C = C + 1, attach C to message, deliver
    def send_message(self, sender, receiver):
        s = self.processes[sender]
        s.clock += 1
        self.msg_count += 1
        msg = Message(f"M{self.msg_count}", sender, receiver, s.clock)
        self.processes[receiver].inbox.append(msg)   # "network" delivery
        self._record(s, "SEND", msg.msg_id)
        return msg

    # Rule 3: receive  ->  C = max(C, T) + 1
    def receive_message(self, receiver, msg=None):
        r = self.processes[receiver]
        if msg is None:
            msg = r.inbox.popleft()
        else:
            r.inbox.remove(msg)
        before = r.clock
        r.clock = max(r.clock, msg.timestamp) + 1
        ev = self._record(r, "RECEIVE", msg.msg_id)
        print(f"       max({before}, {msg.timestamp}) + 1 = {r.clock}")
        return ev

    # ------------------------------------------------------------------
    # Happened-before (->) relation, built from the actual execution:
    #   (a) program order within a process
    #   (b) send(m) -> receive(m)
    #   (c) transitivity
    # Used only to *verify* causality/concurrency, independent of clocks.
    # ------------------------------------------------------------------
    def _happened_before_graph(self):
        edges = {e.event_id: set() for e in self.log}
        for p in self.processes.values():
            for a, b in zip(p.history, p.history[1:]):
                edges[a.event_id].add(b.event_id)
        sends = {e.msg_id: e for e in self.log if e.etype == "SEND"}
        for e in self.log:
            if e.etype == "RECEIVE":
                edges[sends[e.msg_id].event_id].add(e.event_id)
        return edges

    def happened_before(self, a, b):
        edges = self._happened_before_graph()
        stack, seen = [a.event_id], set()
        while stack:
            cur = stack.pop()
            for nxt in edges[cur]:
                if nxt == b.event_id:
                    return True
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return False

    def concurrent(self, a, b):
        return not self.happened_before(a, b) and not self.happened_before(b, a)

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    def print_event_log(self):
        line = "=" * 52
        print("\n" + line)
        print("             LAMPORT LOGICAL CLOCK")
        print(line + "\n")
        print(f"{'Process':<11}{'Event':<9}{'Type':<11}{'Msg':<6}{'Timestamp':>9}")
        print("-" * 52)
        for e in self.log:
            print(f"{e.process:<11}{e.event_id:<9}{e.etype:<11}{e.msg_id:<6}{e.timestamp:>9}")
        print("-" * 52)
        print("Final clocks: " + ", ".join(
            f"{n} = {p.clock}" for n, p in self.processes.items()))

    def print_causal_table(self):
        print("\nCAUSAL ORDERING  (a -> b  implies  L(a) < L(b))")
        print("-" * 72)
        print(f"{'Event A':<18}{'Event B':<20}{'TS A':>6}{'TS B':>6}   Holds?")
        print("-" * 72)
        sends = {e.msg_id: e for e in self.log if e.etype == "SEND"}
        for r in (e for e in self.log if e.etype == "RECEIVE"):
            s = sends[r.msg_id]
            a = f"{s.process} SEND {s.msg_id}"
            b = f"{r.process} RECEIVE {r.msg_id}"
            ok = "YES" if s.timestamp < r.timestamp else "NO"
            print(f"{a:<18}{b:<20}{s.timestamp:>6}{r.timestamp:>6}   {ok}")
        # one transitive chain as well
        first, last = self.log[0], self.log[-1]
        if self.happened_before(first, last):
            a = f"{first.process} {first.etype} {first.event_id}"
            b = f"{last.process} {last.etype} {last.event_id}"
            ok = "YES" if first.timestamp < last.timestamp else "NO"
            print(f"{a:<18}{b:<20}{first.timestamp:>6}{last.timestamp:>6}   {ok}  (transitive)")
        print("-" * 72)

    def print_concurrent_events(self):
        print("\nCONCURRENT EVENTS  (neither a -> b nor b -> a)")
        print("-" * 72)
        print(f"{'Event A':<16}{'Event B':<16}{'TS A':>6}{'TS B':>6}   Note")
        print("-" * 72)
        for a, b in combinations(self.log, 2):
            if a.process != b.process and self.concurrent(a, b):
                if a.timestamp == b.timestamp:
                    note = "same timestamp"
                elif a.timestamp < b.timestamp:
                    note = "L(a)<L(b) but NOT causal"
                else:
                    note = "L(a)>L(b) but NOT causal"
                print(f"{a.process+' '+a.event_id:<16}{b.process+' '+b.event_id:<16}"
                      f"{a.timestamp:>6}{b.timestamp:>6}   {note}")
        print("-" * 72)

    def print_all_relationships(self):
        """Classify every pair of events as CAUSAL or CONCURRENT."""
        print("\nEVENT RELATIONSHIPS  (every pair of events)")
        print("-" * 72)
        print(f"{'Event A':<12}{'Event B':<12}{'L(A)':>5}{'L(B)':>6}   Relationship")
        print("-" * 72)
        causal = concurrent = 0
        for a, b in combinations(self.log, 2):
            ea = f"{a.process} {a.event_id}"
            eb = f"{b.process} {b.event_id}"
            if self.happened_before(a, b):
                rel = f"CAUSAL      ({a.event_id} -> {b.event_id})"
                causal += 1
            elif self.happened_before(b, a):
                rel = f"CAUSAL      ({b.event_id} -> {a.event_id})"
                causal += 1
            else:
                rel = f"CONCURRENT  ({a.event_id} || {b.event_id})"
                concurrent += 1
            print(f"{ea:<12}{eb:<12}{a.timestamp:>5}{b.timestamp:>6}   {rel}")
        print("-" * 72)
        print(f"Total pairs: {causal + concurrent}  |  "
              f"Causal: {causal}  |  Concurrent: {concurrent}")


# ----------------------------------------------------------------------
# Part D - Exercise scenario
# ----------------------------------------------------------------------
def run_exercise():
    print("PART D - EXERCISE SCENARIO")
    print("Initial clocks: P1 = 0, P2 = 0, P3 = 0\n")
    ds = DistributedSystem(["P1", "P2", "P3"])

    ds.local_event("P1")                      # 1. P1 local event E1
    m1 = ds.send_message("P1", "P2")          # 2. P1 sends to P2
    print("\n  Message in transit:\n    " + str(m1).replace("\n", "\n    ") + "\n")
    ds.receive_message("P2", m1)              # 3. P2 receives from P1
    ds.local_event("P2")                      # 4. P2 local event E4
    m2 = ds.send_message("P2", "P3")          # 5. P2 sends to P3
    ds.local_event("P1")                      # 6. P1 local event E6
    m3 = ds.send_message("P1", "P3")          # 7. P1 sends to P3
    ds.receive_message("P3", m2)              # 8. P3 receives from P2
    ds.receive_message("P3", m3)              # 9. P3 receives from P1

    ds.print_event_log()
    ds.print_causal_table()
    ds.print_concurrent_events()
    ds.print_all_relationships()


# ----------------------------------------------------------------------
# Part I - Concurrent events with non-communicating processes
# ----------------------------------------------------------------------
def run_concurrency_demo():
    print("\n\nPART I - NON-COMMUNICATING PROCESSES")
    print("P1:  E1 -------- E2")
    print("P2:  E3 -------- E4\n")
    ds = DistributedSystem(["P1", "P2"])
    e1 = ds.local_event("P1")
    e2 = ds.local_event("P1")
    e3 = ds.local_event("P2")
    e4 = ds.local_event("P2")

    print(f"\n  L(E1) = {e1.timestamp}, L(E4) = {e4.timestamp}  ->  L(E1) < L(E4)")
    print(f"  Is E1 -> E4 ?  {ds.happened_before(e1, e4)}")
    print(f"  Are E1 and E4 concurrent?  {ds.concurrent(e1, e4)}")
    print(f"  L(E1) = L(E3) = {e1.timestamp}, concurrent: {ds.concurrent(e1, e3)}")
    ds.print_all_relationships()

    print("""
  Can Lamport timestamps alone determine whether two events are concurrent?
  NO. Lamport clocks only guarantee  a -> b  =>  L(a) < L(b).
  The converse does not hold: L(a) < L(b) does NOT imply a -> b.
  Above, L(E1) < L(E4) yet E1 and E4 are concurrent (no message links them).
  Equal timestamps (E1, E3) only tell us the events are not causally
  ordered, but in general a single integer cannot distinguish "causally
  before" from "concurrent". Vector clocks solve this: V(a) < V(b) iff a -> b.""")


if __name__ == "__main__":
    run_exercise()
    run_concurrency_demo()  