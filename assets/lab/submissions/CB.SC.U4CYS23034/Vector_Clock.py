def local_event(v, p, event):
    v[p] = v[p] + 1
    print(event, ":", "P" + p, "performs a local event")
    print("Vector =", v)
    print()
    return v
 
def send_msg(v, p, receiver, event):
    v[p] = v[p] + 1
    print(event, ":", "P" + p, "sends a msg to", "P" + receiver)
    print("Vector =", v)
    print("msg timestamp =", v)
    print()
    return v.copy()

def receive_msg(v, p, msg, event):
    for i in range(3):
        v[i] = max(v[i], msg[i])
    v[p] = v[p] + 1
    print(event, ":", "P" + p, "receives a msg")
    print("Vector =", v)
    print()
    return v
    
def compare(v1, v2):
    first = True
    second = True
    for i in range(3):
        if v1[i] > v2[i]:
            first = False
        if v2[i] > v1[i]:
            second = False
    if first and not second:
        print("First event happened before second event")
    elif second and not first:
        print("Second event happened before first event")
    elif first and second:
        print("Both events have the same timestamp")
    else:
        print("Events are concurrent")

P1,P2,P3 = [0]*3, [0]*3, [0]*3
print("Vector Logical Clock")
print()

P1 = local_event(P1, "1", "E1")
M1 = send_msg(P1, "1", "2", "E2")
P2 = receive_msg(P2, 1, M1, "E3")
P2 = local_event(P2, 1, "E4")
M2 = send_msg(P2, 1, 2, "E5")
P1 = local_event(P1, "1", "E6")
M3 = send_msg(P1, "1", "3", "E7")
P3 = receive_msg(P3, 2, M2, "E8")
P3 = receive_msg(P3, 2, M3, "E9")


print("Final Vector Clocks")
print("P1 =", P1)
print("P2 =", P2)
print("P3 =", P3)
print()
