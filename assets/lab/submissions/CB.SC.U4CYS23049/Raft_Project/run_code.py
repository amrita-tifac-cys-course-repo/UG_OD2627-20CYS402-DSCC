import sys

from node import RaftNode

node_id = int(sys.argv[1])

ports = {
    1:5001,
    2:5002,
    3:5003
}

peer_ports = {
    1:[5002,5003],
    2:[5001,5003],
    3:[5001,5002]
}

node = RaftNode(
    node_id,
    ports[node_id],
    peer_ports[node_id]
)

node.run()