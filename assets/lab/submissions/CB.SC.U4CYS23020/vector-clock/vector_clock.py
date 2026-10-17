PROCESSES = {"P1": 0, "P2": 1, "P3": 2}
clocks = {"P1": [0,0,0], "P2": [0,0,0], "P3": [0,0,0]}
event_log = []

def local_event(process, event_id):
    clocks[process][PROCESSES[process]] += 1
    event_log.append((process, event_id, "LOCAL", list(clocks[process])))

def send_message(sender, event_id):
    clocks[sender][PROCESSES[sender]] += 1
    event_log.append((sender, event_id, "SEND", list(clocks[sender])))
    return list(clocks[sender])

def receive_message(receiver, msg_timestamp, event_id):
    for i in range(3):
        clocks[receiver][i] = max(clocks[receiver][i], msg_timestamp[i])
    clocks[receiver][PROCESSES[receiver]] += 1
    event_log.append((receiver, event_id, "RECEIVE", list(clocks[receiver])))

def compare_vectors(v1, v2):
    if v1 == v2: return "=="
    if all(x <= y for x, y in zip(v1, v2)): return "->"
    if all(y <= x for x, y in zip(v1, v2)): return "<-"
    return "||"

local_event("P1", "E1")
m1 = send_message("P1", "E2")
receive_message("P2", m1, "E3")
local_event("P2", "E4")
m2 = send_message("P2", "E5")
local_event("P1", "E6")
m3 = send_message("P1", "E7")
receive_message("P3", m2, "E8")
receive_message("P3", m3, "E9")

print("=" * 56)
print("                 VECTOR CLOCK")
print("=" * 56)
print(f"{'Process':<10} {'Event':<8} {'Type':<11} {'Vector Timestamp'}")
print("-" * 56)
for proc, eid, etype, vc in event_log:
    vc_str = str(vc).replace(" ", "")
    print(f"{proc:<10} {eid:<8} {etype:<11} {vc_str}")
print("-" * 56)

print("=" * 56)
print("           CONCURRENT EVENTS DETECTION")
print("=" * 56)
for i in range(len(event_log)):
    for j in range(i + 1, len(event_log)):
        e1, e2 = event_log[i], event_log[j]
        if compare_vectors(e1[3], e2[3]) == "||":
            v1_s = str(e1[3]).replace(" ", "")
            v2_s = str(e2[3]).replace(" ", "")
            print(f"{e1[1]} {v1_s} || {e2[1]} {v2_s} (Concurrent)")
print("=" * 56)
