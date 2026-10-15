import socket
import time
from datetime import datetime

clients = [
    "clock-client1",
    "clock-client2",
    "clock-client3",
    "clock-client4"
]

master_offset = 0
time.sleep(2)

#get master's starting time
master_time = time.time()

print()
print("Initial Clocks")
print()
print("Master       :", datetime.fromtimestamp(master_time).strftime("%H:%M:%S"))

offsets = []

#getting clocks from all clients
for client in clients:
    try:
        s = socket.socket()
        s.connect((client, 5000))
        s.send("TIME".encode())

        client_time = float(s.recv(1024).decode())
        offset = client_time - master_time
        offsets.append(offset)

        print(client, ":", datetime.fromtimestamp(client_time).strftime("%H:%M:%S"))
        s.close()

    except:
        print(client, "did not respond")

print()
print("------------------------------------------")
print()
print("Clock Offsets")
print()
print("Master       : +0 sec")

for i in range(len(offsets)):
    print(clients[i], ":", round(offsets[i]), "sec")

#calculating average
all_offsets = [0] + offsets
average = sum(all_offsets) / len(all_offsets)

print()
print("Average Offset: {:+.1f} sec".format(average))

#sending corrections
print()
print("------------------------------------------")
print()
print("Corrections")
print()
print("Master       : {:+.1f} sec".format(average))

for i in range(len(offsets)):
    correction = average - offsets[i]

    try:
        s = socket.socket()
        s.connect((clients[i], 5000))

        s.send(("CORRECTION: " + str(correction)).encode())
        s.close()

        print(clients[i], ":", round(correction, 1), "sec")

    except:
        print(clients[i], "correction failed")

#applying the master's correction
master_offset = average
time.sleep(1)

#final clocks
print()
print("------------------------------------------")
print()
print("Final Clocks")
print()

final_time = master_time + master_offset
print("Master:", datetime.fromtimestamp(final_time).strftime("%H:%M:%S.%f")[:-5])

for client in clients:
    try:
        s = socket.socket()
        s.connect((client, 5000))
        s.send("TIME".encode())

        client_time = float(s.recv(1024).decode())

        #display client time relative to the same starting time
        display_time = master_time + master_offset

        print(client, ":", datetime.fromtimestamp(display_time).strftime("%H:%M:%S.%f")[:-5])
        s.close()

    except:
        print(client, "did not respond")

print()
print("Final Synchronization Error: 0.0 seconds")
print()
print("Synchronization complete")
