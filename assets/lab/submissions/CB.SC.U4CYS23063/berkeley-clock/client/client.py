import os
import socket
import time

CLIENT_ID = os.getenv("CLIENT_ID", "client")
CLOCK_OFFSET = float(os.getenv("CLOCK_OFFSET", "0"))

HOST = "0.0.0.0"
PORT = 5000


def get_clock():
    return time.time() + CLOCK_OFFSET


def format_time(timestamp):
    return time.strftime("%H:%M:%S", time.localtime(timestamp))


def main():
    global CLOCK_OFFSET

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"[{CLIENT_ID}] Started")
    print(f"[{CLIENT_ID}] Initial offset: {CLOCK_OFFSET:+.1f} seconds")
    print(f"[{CLIENT_ID}] Listening on port {PORT}")

    while True:
        conn, addr = server.accept()

        data = conn.recv(1024).decode().strip()

        if data == "CLOCK_REQUEST":

            current_clock = get_clock()

            response = f"{current_clock}"

            conn.sendall(response.encode())

            print(
                f"[{CLIENT_ID}] Clock request -> "
                f"{format_time(current_clock)} "
                f"(offset {CLOCK_OFFSET:+.1f}s)"
            )

        elif data.startswith("CORRECTION:"):

            correction = float(data.split(":")[1])

            print(
                f"[{CLIENT_ID}] Received correction: "
                f"{correction:+.2f} seconds"
            )

            CLOCK_OFFSET += correction

            print(
                f"[{CLIENT_ID}] New offset: "
                f"{CLOCK_OFFSET:+.2f} seconds"
            )

            conn.sendall(b"CORRECTION_APPLIED")

        conn.close()


if __name__ == "__main__":
    main()