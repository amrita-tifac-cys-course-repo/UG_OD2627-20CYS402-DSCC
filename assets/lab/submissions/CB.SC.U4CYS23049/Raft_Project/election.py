import random

def start_election(candidate, nodes):

    candidate.become_candidate()

    votes = 1          # Vote for itself

    for node in nodes:

        if node.node_id == candidate.node_id:
            continue

        print(f"Node {candidate.node_id} requests vote from Node {node.node_id}")

        if node.voted_for is None:
            node.voted_for = candidate.node_id
            votes += 1
            print(f"Node {node.node_id} voted YES")

    print(f"\nVotes Received = {votes}")

    if votes > len(nodes)//2:
        candidate.become_leader()
    else:
        print("Election Failed")