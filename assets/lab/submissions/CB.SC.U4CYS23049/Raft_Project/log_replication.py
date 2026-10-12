def replicate_log(leader, nodes, command):

    print(f"\nClient Request : {command}")

    # Leader stores command
    leader.log.append(command)

    print(f"Leader Node {leader.node_id} appended log: {command}")

    acknowledgements = 1   # Leader itself

    for node in nodes:

        if node.node_id != leader.node_id:

            node.log.append(command)

            print(f"Follower {node.node_id} stored log: {command}")

            acknowledgements += 1

    print(f"\nAcknowledgements = {acknowledgements}")

    if acknowledgements > len(nodes)//2:

        leader.commit_index += 1

        print("\nMajority received.")
        print("Log Entry Committed!")

        for node in nodes:
            node.commit_index = leader.commit_index