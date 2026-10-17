class Process:
    def __init__(self, name):
        self.name = name
        self.vector = [0, 0, 0]


class Message:
    def __init__(self, message_id, sender, receiver, vector):
        self.message_id = message_id
        self.sender = sender
        self.receiver = receiver
        self.vector = vector.copy()


processes = {
    "P1": Process("P1"),
    "P2": Process("P2"),
    "P3": Process("P3")
}

process_index = {
    "P1": 0,
    "P2": 1,
    "P3": 2
}

events = []
event_count = 0
message_count = 0

current_process = processes["P1"]


def local_event(process):
    global event_count

    index = process_index[process.name]
    process.vector[index] += 1

    event_count += 1

    events.append(
        (event_count, process.name, "LOCAL",
         "-", process.vector.copy())
    )

    print("\nLOCAL EVENT")
    print(f"Event ID          : E{event_count}")
    print(f"Process           : {process.name}")
    print(f"Vector Clock      : {process.vector}")


def send_message(sender, receiver):
    global event_count, message_count, current_process

    # Increment sender's own vector component
    sender_index = process_index[sender.name]
    sender.vector[sender_index] += 1

    event_count += 1
    message_count += 1

    send_event_id = event_count

    message = Message(
        f"M{message_count}",
        sender.name,
        receiver.name,
        sender.vector
    )

    events.append(
        (event_count, sender.name, "SEND",
         message.message_id, sender.vector.copy())
    )

    print("\nMESSAGE SENT")
    print(f"Message ID        : {message.message_id}")
    print(f"Sender            : {sender.name}")
    print(f"Receiver          : {receiver.name}")
    print(f"Send Event        : E{send_event_id}")
    print(f"Send Vector       : {message.vector}")

    # Merge received vector with receiver's vector
    receiver_index = process_index[receiver.name]

    for i in range(len(receiver.vector)):
        receiver.vector[i] = max(
            receiver.vector[i],
            message.vector[i]
        )

    # Increment receiver's own component
    receiver.vector[receiver_index] += 1

    event_count += 1

    events.append(
        (event_count, receiver.name, "RECEIVE",
         message.message_id, receiver.vector.copy())
    )

    print(f"Receive Event     : E{event_count}")
    print(f"Receive Vector    : {receiver.vector}")

    # Receiver becomes the current process
    current_process = receiver


def show_clocks():
    print("\nCURRENT VECTOR CLOCKS")
    print("-" * 35)

    for process in processes.values():
        print(f"{process.name} = {process.vector}")

    print(f"\nCurrent Process = {current_process.name}")


def show_events():
    if not events:
        print("\nNo events recorded.")
        return

    print("\nEVENT LOG\n")

    print(
        f"{'Event':<8}"
        f"{'Process':<10}"
        f"{'Type':<12}"
        f"{'Message':<10}"
        f"{'Vector Clock':<20}"
    )

    print("-" * 60)

    for number, process, event_type, message_id, vector in events:
        print(
            f"{'E' + str(number):<8}"
            f"{process:<10}"
            f"{event_type:<12}"
            f"{message_id:<10}"
            f"{str(vector):<20}"
        )

    print("-" * 60)


print("=" * 50)
print("        VECTOR CLOCK SIMULATION")
print("=" * 50)

print("\nDistributed Processes:")

for process in processes.values():
    print(f"{process.name} -> Vector Clock = {process.vector}")

print(f"\nCurrent Process -> {current_process.name}")

while True:
    print("\n1. Local Event")
    print("2. Send Message")
    print("3. Show Vector Clocks")
    print("4. Show Event Log")
    print("5. Exit")

    choice = input("\nEnter your choice: ").strip()

    if choice == "1":
        local_event(current_process)

    elif choice == "2":
        receiver_name = input(
            "Enter receiver process (P1/P2/P3): "
        ).strip().upper()

        if receiver_name not in processes:
            print("Invalid receiver process!")
            continue

        if receiver_name == current_process.name:
            print("Receiver cannot be the current process!")
            continue

        receiver = processes[receiver_name]

        send_message(current_process, receiver)

    elif choice == "3":
        show_clocks()

    elif choice == "4":
        show_events()

    elif choice == "5":
        print("\nProgram terminated.")
        break

    else:
        print("Invalid choice!")
