class Process:
    def __init__(self, name, n):
        self.name = name
        self.clock = [0] * n

    def local_event(self):
        self.clock[int(self.name[1:]) - 1] += 1
        return self.clock.copy()

    def send_message(self, receiver):
        self.clock[int(self.name[1:]) - 1] += 1
        message = {
            "sender": self.name,
            "receiver": receiver.name,
            "timestamp": self.clock.copy()
        }
        return message

    def receive_message(self, message):
        for i in range(len(self.clock)):
            self.clock[i] = max(self.clock[i], message["timestamp"][i])
        self.clock[int(self.name[1:]) - 1] += 1
        return self.clock.copy()


def compare_vectors(v1, v2):
    if v1 == v2:
        return "Same timestamp"

    if all(a <= b for a, b in zip(v1, v2)):
        return "V1 happened before V2"

    if all(a >= b for a, b in zip(v1, v2)):
        return "V2 happened before V1"

    return "Concurrent events"


n = int(input("Enter the number of processes: "))

processes = {}

for i in range(1, n + 1):
    name = input(f"Enter process {i} name: ")
    processes[name] = Process(name, n)

events = []

while True:
    print("\n1. Local Event")
    print("2. Send Message")
    print("3. Receive Message")
    print("4. Compare Vector Clocks")
    print("5. Display Processes")
    print("6. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        name = input("Enter process name: ")

        if name in processes:
            timestamp = processes[name].local_event()
            events.append((name, "LOCAL", timestamp.copy()))
            print("Vector Timestamp:", timestamp)
        else:
            print("Invalid process")

    elif choice == "2":
        sender = input("Enter sender process: ")
        receiver = input("Enter receiver process: ")

        if sender in processes and receiver in processes:
            message = processes[sender].send_message(processes[receiver])
            events.append((sender, "SEND", message["timestamp"].copy()))
            print("Message sent:", message)
        else:
            print("Invalid process")

    elif choice == "3":
        receiver = input("Enter receiver process: ")
        sender = input("Enter sender process: ")

        if receiver in processes and sender in processes:
            timestamp = processes[sender].clock.copy()
            message = {
                "sender": sender,
                "receiver": receiver,
                "timestamp": timestamp
            }
            result = processes[receiver].receive_message(message)
            events.append((receiver, "RECEIVE", result.copy()))
            print("Vector Timestamp:", result)
        else:
            print("Invalid process")

    elif choice == "4":
        v1 = list(map(int, input("Enter first vector: ").split()))
        v2 = list(map(int, input("Enter second vector: ").split()))

        if len(v1) == n and len(v2) == n:
            print(compare_vectors(v1, v2))
        else:
            print("Vector size must match the number of processes")

    elif choice == "5":
        for name, process in processes.items():
            print(name, ":", process.clock)

    elif choice == "6":
        break

    else:
        print("Invalid choice")