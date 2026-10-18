class Message:
    def __init__(self, message_id, sender, receiver, timestamp):
        self.message_id = message_id
        self.sender = sender
        self.receiver = receiver
        self.timestamp = timestamp


class Process:
    def __init__(self, process_id):
        self.process_id = process_id
        self.clock = 0
        self.events = []

    def local_event(self, event_id):
        self.clock += 1
        self.events.append((event_id, "LOCAL", self.clock))
        return self.clock

    def send_message(self, receiver, message_id, event_id):
        self.clock += 1
        message = Message(
            message_id,
            self.process_id,
            receiver.process_id,
            self.clock
        )
        self.events.append((event_id, "SEND", self.clock))
        return message

    def receive_message(self, message, event_id):
        self.clock = max(self.clock, message.timestamp) + 1
        self.events.append((event_id, "RECEIVE", self.clock))
        return self.clock


# Create three distributed processes
P1 = Process("P1")
P2 = Process("P2")
P3 = Process("P3")

# Execute the required lab event sequence
P1.local_event("E1")
M1 = P1.send_message(P2, "M1", "E2")
P2.receive_message(M1, "E3")
P2.local_event("E4")
M2 = P2.send_message(P3, "M2", "E5")
P1.local_event("E6")
M3 = P1.send_message(P3, "M3", "E7")
P3.receive_message(M2, "E8")
P3.receive_message(M3, "E9")

# Display the event log
print("=" * 55)
print("              LAMPORT LOGICAL CLOCK")
print("=" * 55)

print("\nInitial Logical Clocks:")
print("P1 = 0")
print("P2 = 0")
print("P3 = 0")

print("\n")
print(f"{'Process':<10}{'Event':<9}{'Type':<12}{'Timestamp'}")
print("-" * 55)

all_events = [
    ("P1", P1.events[0]),
    ("P1", P1.events[1]),
    ("P2", P2.events[0]),
    ("P2", P2.events[1]),
    ("P2", P2.events[2]),
    ("P1", P1.events[2]),
    ("P1", P1.events[3]),
    ("P3", P3.events[0]),
    ("P3", P3.events[1]),
]

for process, event in all_events:
    print(f"{process:<10}{event[0]:<9}{event[1]:<12}{event[2]}")

print("-" * 55)
print("\nFinal Logical Clocks:")
print("P1 =", P1.clock)
print("P2 =", P2.clock)
print("P3 =", P3.clock)
