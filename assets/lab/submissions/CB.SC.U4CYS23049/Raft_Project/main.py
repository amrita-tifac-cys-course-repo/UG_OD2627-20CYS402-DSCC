from node import Node
from election import start_election
from heartbeat import send_heartbeats
from log_replication import replicate_log

import threading
import time

node1 = Node(1,[2,3])
node2 = Node(2,[1,3])
node3 = Node(3,[1,2])

nodes = [node1,node2,node3]

print("Starting Cluster...\n")

start_election(node1,nodes)

if node1.state=="Leader":

    thread = threading.Thread(
        target=send_heartbeats,
        args=(node1,nodes),
        daemon=True
    )

    thread.start()

    time.sleep(2)

    replicate_log(node1,nodes,"SET X = 100")

time.sleep(5)

print("\nFinal Node Status\n")

for node in nodes:

    node.display()