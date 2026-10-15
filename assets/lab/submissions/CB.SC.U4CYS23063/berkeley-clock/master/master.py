import socket
import time


CLIENTS = {
    "client1": "clock-client1",
    "client2": "clock-client2",
    "client3": "clock-client3",
    "client4": "clock-client4",
}

PORT = 5000


def get_master_clock():
    return time.time()


def format_time(timestamp):
    return time.strftime("%H:%M:%S", time.localtime(timestamp))


def request_clock(host):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        sock.connect((host, PORT))
        sock.sendall(b"CLOCK_REQUEST")

        data = sock.recv(1024).decode()

        sock.close()

        return float(data)

    except Exception as e:
        print(f"Error contacting {host}: {e}")
        return None


def send_correction(host, correction):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        sock.connect((host, PORT))

        message = f"CORRECTION:{correction}"

        sock.sendall(message.encode())

        response = sock.recv(1024).decode()

        sock.close()

        return response

    except Exception as e:
        print(f"Error sending correction to {host}: {e}")
        return None


def main():

    print()
    print("=" * 55)
    print("       BERKELEY CLOCK SYNCHRONIZATION")
    print("=" * 55)

    master_clock = get_master_clock()

    print("\nInitial Clocks")
    print("-" * 55)

    print(
        f"Master   : "
        f"{format_time(master_clock)}"
    )

    clocks = {}

    # Poll clients
    for client_id, hostname in CLIENTS.items():

        clock = request_clock(hostname)

        if clock is not None:
            clocks[client_id] = clock

            print(
                f"{client_id:<10}: "
                f"{format_time(clock)}"
            )

    print("\nClock Offsets")
    print("-" * 55)

    offsets = {}

    # Master offset = 0
    offsets["Master"] = 0.0

    print("Master     : +0.00 sec")

    for client_id, clock in clocks.items():

        offset = clock - master_clock

        offsets[client_id] = offset

        print(
            f"{client_id:<10}: "
            f"{offset:+.2f} sec"
        )

    # Calculate average
    total_offset = sum(offsets.values())
    average_offset = total_offset / len(offsets)

    print("\nAverage Offset")
    print("-" * 55)

    print(
        f"Average Offset: "
        f"{average_offset:+.2f} sec"
    )

    # Calculate corrections
    print("\nCorrections")
    print("-" * 55)

    master_correction = average_offset

    print(
        f"Master     : "
        f"{master_correction:+.2f} sec"
    )

    for client_id, hostname in CLIENTS.items():

        if client_id not in offsets:
            continue

        correction = average_offset - offsets[client_id]

        print(
            f"{client_id:<10}: "
            f"{correction:+.2f} sec"
        )

        send_correction(hostname, correction)

    # Apply correction to master
    master_clock += master_correction

    print("\nFinal Clocks")
    print("-" * 55)

    print(
        f"Master     : "
        f"{format_time(master_clock)}"
    )

    # Read final clocks from clients
    for client_id, hostname in CLIENTS.items():

        final_clock = request_clock(hostname)

        if final_clock is not None:

            print(
                f"{client_id:<10}: "
                f"{format_time(final_clock)}"
            )

    print()
    print("=" * 55)
    print("Synchronization completed.")
    print("=" * 55)


if __name__ == "__main__":
    main()