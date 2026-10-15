class Process:
    def __init__(self, name, index, events):
        self.name = name
        self.index = index
        self.vector = [0, 0, 0]
        self.events = events
        self.received = set()

    def record(self, kind, message=None):
        event = {"event": f"E{len(self.events) + 1}", "process": self.name,
                 "type": kind, "message": message["id"] if message else "-",
                 "timestamp": self.vector.copy()}
        self.events.append(event)
        return event

    def local_event(self):
        self.vector[self.index] += 1
        return self.record("LOCAL")

    def send_message(self, receiver, message_id):
        if receiver == self.name:
            raise ValueError("Choose a different receiver")
        self.vector[self.index] += 1
        message = {"id": message_id, "sender": self.name,
                   "receiver": receiver, "timestamp": self.vector.copy()}
        self.record("SEND", message)
        return message

    def receive_message(self, message):
        if message["receiver"] != self.name or message["id"] in self.received:
            raise ValueError("Wrong receiver or message already received")
        incoming = message["timestamp"]
        if len(incoming) != len(self.vector) or any(type(value) is not int or value < 0 for value in incoming):
            raise ValueError("Invalid vector timestamp")
        self.vector = [max(local, remote) for local, remote in zip(self.vector, incoming)]
        self.vector[self.index] += 1
        self.received.add(message["id"])
        return self.record("RECEIVE", message)


def compare_vectors(first, second):
    if len(first) != len(second) or any(type(value) is not int or value < 0 for value in first + second):
        raise ValueError("Vectors must have equal sizes and nonnegative integers")
    if first == second:
        return "same timestamp"
    if all(a <= b for a, b in zip(first, second)):
        return "happened before"
    if all(a >= b for a, b in zip(first, second)):
        return "happened after"
    return "is concurrent with"


def simulate():
    events = []
    p1, p2, p3 = [Process(f"P{index + 1}", index, events) for index in range(3)]
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
    print("VECTOR CLOCK\n")
    print(f"{'Event':<8} {'Process':<10} {'Type':<10} {'Message':<10} Vector")
    for event in events:
        print(f"{event['event']:<8} {event['process']:<10} {event['type']:<10} "
              f"{event['message']:<10} {event['timestamp']}")
    print("\nCAUSAL RELATIONSHIPS")
    history = {event["event"]: event["timestamp"] for event in events}
    for first, second in (("E1", "E2"), ("E2", "E3"), ("E5", "E8"), ("E2", "E8"), ("E6", "E4"), ("E7", "E5")):
        relation = compare_vectors(history[first], history[second])
        print(f"{first} {history[first]} {relation} {second} {history[second]}")


if __name__ == "__main__":
    main()
