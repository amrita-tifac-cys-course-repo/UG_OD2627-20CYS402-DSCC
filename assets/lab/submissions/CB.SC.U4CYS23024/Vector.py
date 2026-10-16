"""
Lab #7 - Vector Clock
20CYS402 - Distributed Systems and Cloud Computing

Simulates 3 distributed processes (P1, P2, P3). Each process keeps a
vector clock V[0..N-1] (one entry per process). Supports LOCAL, SEND and
RECEIVE events, computes vector timestamps dynamically, and uses vector
comparison alone to classify every pair of events as CAUSAL or CONCURRENT.

Rules (process Pi, index i):
  LOCAL   : V[i] = V[i] + 1
  SEND    : V[i] = V[i] + 1, attach a copy of V to the message
  RECEIVE : V[k] = max(V[k], T[k]) for every k, then V[i] = V[i] + 1

Comparison:
  a -> b      iff  V(a) <= V(b) element-wise  and  V(a) != V(b)
  a || b      iff  neither V(a) -> V(b) nor V(b) -> V(a)
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
    timestamp: list         # copy of the sender's vector clock

    def __str__(self):
        return (f"Message ID       : {self.msg_id}\n"
                f"Sender           : {self.sender}\n"
                f"Receiver         : {self.receiver}\n"
                f"Vector Timestamp : {fmt(self.timestamp)}")


@dataclass
class Event:
    event_id: str
    process: str
    etype: str              # LOCAL / SEND / RECEIVE
    vector: list            # vector timestamp of this event
    msg_id: str = ""


class Process:
    """A simulated distributed process with its own vector clock."""

    def __init__(self, name, index, n):
        self.name = name
        self.index = index          # position of this process in the vector
        self.clock = [0] * n        # [0, 0, ..., 0]
        self.inbox = deque()


def fmt(v):
    return "[" + ", ".join(str(x) for x in v) + "]"


# ----------------------------------------------------------------------
# Vector comparison
# ----------------------------------------------------------------------
def happened_before(va, vb):
    """True if va -> vb  (va <= vb element-wise and va != vb)."""
    return all(a <= b for a, b in zip(va, vb)) and va != vb


def concurrent(va, vb):
    return not happened_before(va, vb) and not happened_before(vb, va)


# ----------------------------------------------------------------------
# Distributed system simulator
# ----------------------------------------------------------------------
class DistributedSystem:
    def __init__(self, process_names):
        n = len(process_names)
        self.processes = {name: Process(name, i, n)
                          for i, name in enumerate(process_names)}
        self.log = []
        self.event_count = 0
        self.msg_count = 0

    def _record(self, proc, etype, msg_id=""):
        self.event_count += 1
        ev = Event(f"E{self.event_count}", proc.name, etype,
                   proc.clock.copy(), msg_id)       # snapshot, not a reference
        self.log.append(ev)
        extra = f" ({msg_id})" if msg_id else ""
        print(f"  {ev.event_id:<4} {proc.name}: {etype:<8}{extra:<6} -> V{proc.name[1:]} = {fmt(proc.clock)}")
        return ev

    # Rule 1: local event -> V[i] += 1
    def local_event(self, pname):
        p = self.processes[pname]
        p.clock[p.index] += 1
        return self._record(p, "LOCAL")

    # Rule 2: send -> V[i] += 1, attach copy of V, deliver
    def send_message(self, sender, receiver):
        s = self.processes[sender]
        s.clock[s.index] += 1
        self.msg_count += 1
        msg = Message(f"M{self.msg_count}", sender, receiver, s.clock.copy())
        self.processes[receiver].inbox.append(msg)
        self._record(s, "SEND", msg.msg_id)
        return msg

    # Rule 3: receive -> V[k] = max(V[k], T[k]) for all k, then V[i] += 1
    def receive_message(self, receiver, msg=None):
        r = self.processes[receiver]
        if msg is None:
            msg = r.inbox.popleft()
        else:
            r.inbox.remove(msg)
        before = r.clock.copy()
        r.clock = [max(a, b) for a, b in zip(r.clock, msg.timestamp)]
        merged = r.clock.copy()
        r.clock[r.index] += 1
        ev = self._record(r, "RECEIVE", msg.msg_id)
        print(f"       max({fmt(before)}, {fmt(msg.timestamp)}) = {fmt(merged)}"
              f"  -> V{receiver[1:]}[{r.index + 1}] + 1 = {fmt(r.clock)}")
        return ev

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    def print_event_log(self):
        line = "=" * 56
        print("\n" + line)
        print("                  VECTOR CLOCK")
        print(line + "\n")
        print(f"{'Process':<10}{'Event':<8}{'Type':<10}{'Msg':<6}{'Vector Timestamp':>18}")
        print("-" * 56)
        for e in self.log:
            print(f"{e.process:<10}{e.event_id:<8}{e.etype:<10}{e.msg_id:<6}{fmt(e.vector):>18}")
        print("-" * 56)
        print("Final clocks: " + ", ".join(
            f"{n} = {fmt(p.clock)}" for n, p in self.processes.items()))

    def print_causal_table(self):
        print("\nCAUSAL ORDERING  (a -> b  iff  V(a) < V(b))")
        print("-" * 72)
        print(f"{'Event A':<17}{'Event B':<20}{'V(A)':>11}{'V(B)':>12}   Holds?")
        print("-" * 72)
        sends = {e.msg_id: e for e in self.log if e.etype == "SEND"}
        for r in (e for e in self.log if e.etype == "RECEIVE"):
            s = sends[r.msg_id]
            a = f"{s.process} SEND {s.msg_id}"
            b = f"{r.process} RECEIVE {r.msg_id}"
            ok = "YES" if happened_before(s.vector, r.vector) else "NO"
            print(f"{a:<17}{b:<20}{fmt(s.vector):>11}{fmt(r.vector):>12}   {ok}")
        print("-" * 72)

    def print_concurrent_events(self):
        print("\nCONCURRENT EVENTS  (neither V(a) < V(b) nor V(b) < V(a))")
        print("-" * 72)
        print(f"{'Event A':<14}{'Event B':<14}{'V(A)':>12}{'V(B)':>12}   Why")
        print("-" * 72)
        for a, b in combinations(self.log, 2):
            if concurrent(a.vector, b.vector):
                # show one index where A is bigger and one where B is bigger
                ia = next(k for k in range(len(a.vector)) if a.vector[k] > b.vector[k])
                ib = next(k for k in range(len(a.vector)) if b.vector[k] > a.vector[k])
                why = f"A[{ia+1}]>B[{ia+1}], B[{ib+1}]>A[{ib+1}]"
                print(f"{a.process+' '+a.event_id:<14}{b.process+' '+b.event_id:<14}"
                      f"{fmt(a.vector):>12}{fmt(b.vector):>12}   {why}")
        print("-" * 72)

    def print_all_relationships(self):
        print("\nEVENT RELATIONSHIPS  (every pair, decided from vectors alone)")
        print("-" * 72)
        print(f"{'Event A':<10}{'Event B':<10}{'V(A)':>12}{'V(B)':>12}   Relationship")
        print("-" * 72)
        causal = conc = 0
        for a, b in combinations(self.log, 2):
            if happened_before(a.vector, b.vector):
                rel = f"CAUSAL      ({a.event_id} -> {b.event_id})"
                causal += 1
            elif happened_before(b.vector, a.vector):
                rel = f"CAUSAL      ({b.event_id} -> {a.event_id})"
                causal += 1
            else:
                rel = f"CONCURRENT  ({a.event_id} || {b.event_id})"
                conc += 1
            print(f"{a.process+' '+a.event_id:<10}{b.process+' '+b.event_id:<10}"
                  f"{fmt(a.vector):>12}{fmt(b.vector):>12}   {rel}")
        print("-" * 72)
        print(f"Total pairs: {causal + conc}  |  Causal: {causal}  |  Concurrent: {conc}")


# ----------------------------------------------------------------------
# Exercise scenario (same sequence as the Lamport lab)
# ----------------------------------------------------------------------
def run_exercise():
    print("EXERCISE SCENARIO")
    print("Initial clocks: P1 = [0, 0, 0], P2 = [0, 0, 0], P3 = [0, 0, 0]\n")
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
# Non-communicating processes: vector clocks detect concurrency directly
# ----------------------------------------------------------------------
def run_concurrency_demo():
    print("\n\nNON-COMMUNICATING PROCESSES")
    print("P1:  E1 -------- E2")
    print("P2:  E3 -------- E4\n")
    ds = DistributedSystem(["P1", "P2"])
    e1 = ds.local_event("P1")
    ds.local_event("P1")
    ds.local_event("P2")
    e4 = ds.local_event("P2")

    print(f"\n  V(E1) = {fmt(e1.vector)}, V(E4) = {fmt(e4.vector)}")
    print(f"  V(E1) < V(E4)?  {happened_before(e1.vector, e4.vector)}")
    print(f"  V(E4) < V(E1)?  {happened_before(e4.vector, e1.vector)}")
    print(f"  => E1 || E4 (concurrent): {concurrent(e1.vector, e4.vector)}")
    ds.print_all_relationships()

    print("""
  Can vector timestamps alone determine whether two events are concurrent?
  YES. Vector clocks satisfy  a -> b  <=>  V(a) < V(b)  (both directions).
  With Lamport clocks, L(E1)=1 < L(E4)=2 wrongly suggests an ordering;
  with vector clocks, [1, 0] and [0, 2] are incomparable, so E1 || E4
  is detected from the timestamps themselves, with no extra information.""")


if __name__ == "__main__":
    run_exercise()
    run_concurrency_demo()