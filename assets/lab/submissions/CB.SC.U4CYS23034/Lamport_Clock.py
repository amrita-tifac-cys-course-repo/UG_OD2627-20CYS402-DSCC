def local_event(c, p, event, clock):

    c = c + 1

    print(p, event, "performs a local event")

    print(clock, "=", c)

    print()

    return c


 

def send_msg(c, p, receiver, event, clock):

    c = c + 1

    print(p, event, "sends a msg to", receiver)

    print(clock, "=", c)

    print("msg timestamp =", c)

    print()

    return c


 

def receive_msg(c, p, msg, event, clock):

    c = max(c, msg) + 1

    print(p, event, "receives a msg")

    print(clock, "=", c)

    print()

    return c


 

a, b, c = 0, 0, 0

 

print("Lamport Logical Clock")

print()

 

a = local_event(a, "P1", "E1", "C1") #E1

 

m1 = send_msg(a, "P1", "P2", "E2", "C1") #E2

a = m1

 

b = receive_msg(b, "P2", m1, "E3", "C2") #E3

 

b = local_event(b, "P2", "E4", "C2") #E4

 

m2 = send_msg(b, "P2", "P3", "E5", "C2")

b = m2

 

a = local_event(a, "P1", "E6", "C1")

 

m3 = send_msg(a, "P1", "P3", "E7", "C1")

a = m3

 

c = receive_msg(c, "P3", m2, "E8", "C3")

 

c = receive_msg(c, "P3", m3, "E9", "C3")


 

print("Final Clock Values")

print("C1 =", a)

print("C2 =", b)

print("C3 =", c)
