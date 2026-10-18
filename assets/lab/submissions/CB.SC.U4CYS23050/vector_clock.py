from dataclasses import dataclass
from typing import List, Dict, Tuple

Vector = List[int]


@dataclass
class Message:
    message_id: str
    sender: str
    receiver: str
    timestamp: Vector


class Process:
    def __init__(self, name: str, index: int, process_count: int):
        self.name = name
        self.index = index
        self.clock = [0] * process_count


class VectorClockSimulation:
    def __init__(self, process_names: List[str]):
        self.processes: Dict[str, Process] = {
            name: Process(name, i, len(process_names))
            for i, name in enumerate(process_names)
        }
        self.events = []
        self.messages: Dict[str, Message] = {}
        self.event_number = 0

    def _record(self, process: Process, event_type: str, message: str = "-") -> Vector:
        self.event_number += 1
        timestamp = process.clock.copy()
        event_id = f"E{self.event_number}"
        self.events.append({
            "event": event_id,
            "process": process.name,
            "type": event_type,
            "message": message,
            "timestamp": timestamp,
        })
        print(f"{process.name:<9} {event_id:<7} {event_type:<9} {message:<13} {timestamp}")
        return timestamp

    def local_event(self, process_name: str) -> Vector:
        process = self.processes[process_name]
        process.clock[process.index] += 1
        return self._record(process, "LOCAL")

    def send_message(self, sender_name: str, receiver_name: str, message_id: str) -> Message:
        sender = self.processes[sender_name]
        sender.clock[sender.index] += 1
        timestamp = sender.clock.copy()
        message = Message(message_id, sender_name, receiver_name, timestamp)
        self.messages[message_id] = message
        self._record(sender, "SEND", f"{sender_name}->{receiver_name} ({message_id})")
        return message

    def receive_message(self, receiver_name: str, message_id: str) -> Vector:
        receiver = self.processes[receiver_name]
        message = self.messages[message_id]
        if message.receiver != receiver_name:
            raise ValueError(f"{message_id} is addressed to {message.receiver}, not {receiver_name}")
        receiver.clock = [
            max(local, incoming)
            for local, incoming in zip(receiver.clock, message.timestamp)
        ]
        receiver.clock[receiver.index] += 1
        return self._record(receiver, "RECEIVE", f"{message.sender}->{receiver_name} ({message_id})")


def compare_vectors(a: Vector, b: Vector) -> str:
    """Return causal order, concurrency, or equality for two vector timestamps."""
    a_le_b = all(x <= y for x, y in zip(a, b))
    b_le_a = all(y <= x for x, y in zip(a, b))
    if a_le_b and b_le_a:
        return "same timestamp"
    if a_le_b:
        return "A happened before B (A -> B)"
    if b_le_a:
        return "B happened before A (B -> A)"
    return "concurrent (A || B)"


def is_before(a: Vector, b: Vector) -> bool:
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def main():
    sim = VectorClockSimulation(["P1", "P2", "P3"])
    print("=" * 76)
    print("                         VECTOR CLOCK")
    print("=" * 76)
    print(f"{'Process':<9} {'Event':<7} {'Type':<9} {'Message':<13} Vector Timestamp")
    print("-" * 76)

    # Required scenario from the lab handout.
    sim.local_event("P1")                          # E1
    sim.send_message("P1", "P2", "M1")            # E2
    sim.receive_message("P2", "M1")                # E3
    sim.local_event("P2")                          # E4
    sim.send_message("P2", "P3", "M2")            # E5
    sim.local_event("P1")                          # E6
    sim.send_message("P1", "P3", "M3")            # E7
    sim.receive_message("P3", "M2")                # E8
    sim.receive_message("P3", "M3")                # E9

    by_id = {event["event"]: event for event in sim.events}
    print("-" * 76)
    print("\nVECTOR TIMESTAMP COMPARISONS")
    checks = [
        ("E1", "E2", "Same-process ordering"),
        ("E2", "E3", "Message-based causality"),
        ("E5", "E8", "Message-based causality"),
        ("E6", "E4", "Concurrent events"),
        ("E7", "E5", "Concurrent events"),
        ("E2", "E8", "Transitive causality"),
    ]
    for a_id, b_id, description in checks:
        a = by_id[a_id]["timestamp"]
        b = by_id[b_id]["timestamp"]
        print(f"{description}: {a_id} {a} vs {b_id} {b} -> {compare_vectors(a, b)}")

    # Required explicit demonstration of a concurrent pair.
    a = by_id["E6"]["timestamp"]
    b = by_id["E4"]["timestamp"]
    assert not is_before(a, b) and not is_before(b, a)
    assert is_before(by_id["E2"]["timestamp"], by_id["E3"]["timestamp"])
    assert is_before(by_id["E5"]["timestamp"], by_id["E8"]["timestamp"])
    print("\nAll vector-clock assertions passed.")


if __name__ == "__main__":
    main()
