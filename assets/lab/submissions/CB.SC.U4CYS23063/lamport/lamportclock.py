class Process:
    def __init__(self, name):
        self.name = name
        self.clock = 0

    def local_event(self):
        self.clock += 1
        return self.clock

    def send(self):
        self.clock += 1
        return self.clock

    def receive(self, timestamp):
        self.clock = max(self.clock, timestamp) + 1
        return self.clock


n = int(input("Enter the no of processes: "))

processes = {}

for i in range(1, n + 1):
    processes[f"P{i}"] = Process(f"P{i}")

events = int(input("Enter number of events: "))

for i in range(1, events + 1):
    print("\nEvent", i)
    print("1. LOCAL")
    print("2. SEND")
    print("3. RECEIVE")

    choice = int(input("Enter event type: "))
    process_name = input("Enter process: ")
    process = processes[process_name]

    if choice == 1:
        timestamp = process.local_event()
        print(process_name, "LOCAL", "Timestamp:", timestamp)

    elif choice == 2:
        receiver_name = input("Enter receiver process: ")
        timestamp = process.send()
        print(process_name, "SEND ->", receiver_name, "Timestamp:", timestamp)

    elif choice == 3:
        sender_name = input("Enter sender process: ")
        received_timestamp = int(input("Enter received message timestamp: "))
        timestamp = process.receive(received_timestamp)
        print(process_name, "RECEIVE <-", sender_name, "Timestamp:", timestamp)

    else:
        print("Invalid event type")