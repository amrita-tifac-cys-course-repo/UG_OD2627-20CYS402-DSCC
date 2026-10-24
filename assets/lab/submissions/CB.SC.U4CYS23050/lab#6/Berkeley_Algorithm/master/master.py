import socket
import time

PORT = 5000

CLIENTS = {
    "client1": ("clock-client1", 5000),
    "client2": ("clock-client2", 5000),
    "client3": ("clock-client3", 5000),
    "client4": ("clock-client4", 5000)
}

master_offset = 0.0


def get_master_clock():
    return time.time() + master_offset


def format_clock(timestamp):
    return time.strftime("%H:%M:%S", time.localtime(timestamp))


def get_client_clock(host, port):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect((host, port))

        start_time = time.time()

        client.send(b"CLOCK_REQUEST")
        data = client.recv(1024)

        end_time = time.time()

        client.close()

        client_clock = float(data.decode())

        return client_clock, end_time - start_time

    except Exception as e:
        print(f"Could not contact {host}: {e}")
        return None, None


def send_correction(host, port, correction):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect((host, port))

        message = f"CORRECTION:{correction}"
        client.send(message.encode())

        client.close()

    except Exception as e:
        print(f"Could not send correction to {host}: {e}")


print()
print("==========================================")
print("       BERKELEY CLOCK SYNCHRONIZATION")
print("==========================================")
print()

time.sleep(3)

master_time = get_master_clock()

print("Initial Clocks")
print("------------------------------------------")
print(f"Master   : {format_clock(master_time)}")

clock_data = {
    "Master": master_time
}

for client_name, (host, port) in CLIENTS.items():

    client_clock, rtt = get_client_clock(host, port)

    if client_clock is not None:

        print(
            f"{client_name:<9}: "
            f"{format_clock(client_clock)}"
        )

        clock_data[client_name] = client_clock

    else:

        print(
            f"{client_name:<9}: NO RESPONSE"
        )

print()
print("------------------------------------------")
print("Clock Offsets")
print("------------------------------------------")

master_time = clock_data["Master"]

offsets = {}

master_offset_value = 0.0
offsets["Master"] = master_offset_value

print("Master   : +0.00 sec")

for client_name in CLIENTS:

    if client_name in clock_data:

        offset = clock_data[client_name] - master_time
        offsets[client_name] = offset

        print(
            f"{client_name:<9}: "
            f"{offset:+.2f} sec"
        )

print()
print("------------------------------------------")

total_offset = sum(offsets.values())
number_of_nodes = len(offsets)

average_offset = total_offset / number_of_nodes

print(f"Average Offset: {average_offset:+.2f} sec")

print()
print("------------------------------------------")
print("Corrections")
print("------------------------------------------")

corrections = {}

for node, offset in offsets.items():

    correction = average_offset - offset
    corrections[node] = correction

    print(
        f"{node:<9}: "
        f"{correction:+.2f} sec"
    )

print()
print("------------------------------------------")
print("Applying Corrections")
print("------------------------------------------")

for client_name, (host, port) in CLIENTS.items():

    if client_name in corrections:

        correction = corrections[client_name]

        send_correction(
            host,
            port,
            correction
        )

        print(
            f"{client_name}: "
            f"{correction:+.2f} sec sent"
        )

master_correction = corrections["Master"]

master_offset += master_correction

print(
    f"Master: "
    f"{master_correction:+.2f} sec applied"
)

time.sleep(2)

print()
print("------------------------------------------")
print("Final Clocks")
print("------------------------------------------")

final_master_time = get_master_clock()

print(
    f"Master   : "
    f"{format_clock(final_master_time)}"
)

for client_name, offset in offsets.items():

    if client_name != "Master":

        final_clock = final_master_time

        print(
            f"{client_name:<9}: "
            f"{format_clock(final_clock)}"
        )

print()
print("==========================================")
print("Synchronization Complete")
print("==========================================")