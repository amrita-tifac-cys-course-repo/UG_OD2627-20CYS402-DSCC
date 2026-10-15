import socket 
import time 
import os 
 
client_id = os.getenv("CLIENT_ID", "client") 
clock_offset = float(os.getenv("CLOCK_OFFSET", "0")) 
 
#creating server 
server = socket.socket() 
server.bind(("0.0.0.0", 5000)) 
server.listen(5) 
 
print(client_id, "is running") 
print("Initial offset: ", clock_offset, "seconds") 
 
while True: 
    #waiting for the master
    connection, address = server.accept() 
 
    request = connection.recv(1024).decode() 
 
    #send the current clock
    if request == "TIME": 
        current_time = time.time() + clock_offset 
        connection.send(str(current_time).encode()) 
        print(client_id, "sent clock") 
 
    #receive correction
    elif request.startswith("CORRECTION: "): 
        correction = float(request.split(":")[1]) 
        clock_offset = clock_offset + correction 
 
        print(client_id, "correction: ", round(correction, 2), "seconds") 
        print("New offset: ", round(clock_offset, 2), "seconds") 
 
    connection.close()
