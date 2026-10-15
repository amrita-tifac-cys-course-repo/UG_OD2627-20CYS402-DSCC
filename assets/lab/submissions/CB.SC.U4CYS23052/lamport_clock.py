lass Process:
    def __init__(self, name, events):
        self.name = name
        self.clock = 0
        self.events = events
        self.previous = None
        self.received = set()

    def record(self, kind, message=None):
        parents = [] if self.previous is None else [self.previous]
        if kind == "RECEIVE":
            parents.append(message["send_event"])
        event = {"event": f"E{len(self.events) + 1}", "process": self.name,
                 "type": kind, "message": message["id"] if message else "-",
                 "timestamp": self.clock, "parents": parents}
        self.events.append(event)
        self.previous = event["event"]
        return event

    def local_event(self):
        self.clock += 1
        return self.record("LOCAL")

    def send_message(self, receiver, message_id):
        if receiver == self.name:
            raise ValueError("Choose a different receiver")
        self.clock += 1
        message = {"id": message_id, "sender": self.name,
                   "receiver": receiver, "timestamp": self.clock}
        message["send_event"] = self.record("SEND", message)["event"]
        return message

    def receive_message(self, message):
        if message["receiver"] != self.name or message["id"] in self.received:
            raise ValueError("Wrong receiver or message already received")
        self.clock = max(self.clock, message["timestamp"]) + 1
        self.received.add(message["id"])
        return self.record("RECEIVE", message)


def happened_before(events, first, second):
    history = {event["event"]: event["parents"] for event in events}
    pending = list(history[second])
    visited = set()
    while pending:
        event = pending.pop()
        if event == first:
            return True
        if event not in visited:
            visited.add(event)
            pending.extend(history[event])
    return False


def simulate():
    events = []
    p1, p2, p3 = [Process(name, events) for name in ("P1", "P2", "P3")]
    p1.local_event()
    m1 = p1.send_message("P2", "M1")
    p2.receive_message(m1)
    p2.local_event()
    m2 = p2.send_message("P3", "M2")
    p1.local_event()
    m3 = p1.send_message("P3", "M3")
    p3.receive_message(m2)
    p3.receive_message(m3)
    return events


def main():
    events = simulate()
    print("LAMPORT CLOCK\n")
    print(f"{'Event':<8} {'Process':<10} {'Type':<10} {'Message':<10} {'Timestamp':>10}")
    for event in events:
        print(f"{event['event']:<8} {event['process']:<10} {event['type']:<10} "
              f"{event['message']:<10} {event['timestamp']:>10}")
    print("\nCAUSAL RELATIONSHIPS")
    for first, second in (("E1", "E2"), ("E2", "E3"), ("E5", "E8"), ("E2", "E8"), ("E4", "E6")):
        if happened_before(events, first, second):
            relation = "happened before"
        elif happened_before(events, second, first):
            relation = "happened after"
        else:
            relation = "is concurrent with"
        print(f"{first} {relation} {second}")
    print("\nConcurrency is checked using event history. Lamport timestamps alone cannot prove it.")
    ordered = sorted(events, key=lambda event: (event["timestamp"], event["process"]))
    print("Total order (timestamp, process): " + ", ".join(event["event"] for event in ordered))


if __name__ == "__main__":
    main()
