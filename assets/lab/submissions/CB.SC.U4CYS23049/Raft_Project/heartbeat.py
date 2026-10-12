import threading
import time

def send_heartbeats(leader, nodes):

    while leader.state == "Leader":

        print(f"\nLeader Node {leader.node_id} is sending heartbeats...")

        for node in nodes:

            if node.node_id != leader.node_id:
                node.receive_heartbeat(leader.current_term)

        time.sleep(2)