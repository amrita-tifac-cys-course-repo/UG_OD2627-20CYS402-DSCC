from flask import Flask, request, jsonify
import threading
import time
import random
import requests


class RaftNode:

    def __init__(self, node_id, port, peers):

        self.node_id = node_id
        self.port = port
        self.peers = peers

        # Raft State
        self.state = "Follower"
        self.term = 0
        self.voted_for = None

        # Log
        self.log = []

        # Commit Information
        self.commit_index = -1
        self.last_applied = -1

        # State Machine
        self.state_machine = {}

        # Heartbeat
        self.last_heartbeat = time.time()

        self.app = Flask(__name__)

        self.routes()

        threading.Thread(target=self.election_timer, daemon=True).start()

    # ---------------------------------------------------
    # Routes
    # ---------------------------------------------------
    def routes(self):

        @self.app.route("/vote", methods=["POST"])
        def vote():

            data = request.json

            if self.voted_for is None:

                self.voted_for = data["candidate"]

                print(f"Node {self.node_id} voted for Node {data['candidate']}")

                return jsonify({"vote": True})

            return jsonify({"vote": False})

        @self.app.route("/heartbeat", methods=["POST"])
        def heartbeat():

            self.last_heartbeat = time.time()

            if self.state != "Follower":
                self.state = "Follower"

            return jsonify({"status": "ok"})

        @self.app.route("/append", methods=["POST"])
        def append():

            data = request.json

            command = data["command"]

            self.log.append(command)

            self.commit_index += 1

            self.apply_log(command)

            print(f"Node {self.node_id} stored log: {command}")

            return jsonify({"success": True})

        @self.app.route("/client", methods=["POST"])
        def client():

            if self.state != "Leader":

                return jsonify({
                    "status": "Not Leader"
                })

            data = request.json

            self.replicate_log(data["command"])

            return jsonify({
                "status": "Committed"
            })

        @self.app.route("/status", methods=["GET"])
        def status():

            return jsonify({
                "node": self.node_id,
                "state": self.state,
                "term": self.term,
                "commit_index": self.commit_index,
                "log": self.log,
                "state_machine": self.state_machine
            })

    # ---------------------------------------------------
    # Election Timer
    # ---------------------------------------------------
    def election_timer(self):

        while True:

            timeout = random.randint(5, 10)

            time.sleep(1)

            if self.state == "Leader":
                continue

            if time.time() - self.last_heartbeat > timeout:

                self.start_election()

    # ---------------------------------------------------
    # Leader Election
    # ---------------------------------------------------
    def start_election(self):

        self.state = "Candidate"

        self.term += 1

        self.voted_for = self.node_id

        votes = 1

        print(f"\nNode {self.node_id} started Election")

        for peer in self.peers:

            try:

                response = requests.post(
                    f"http://127.0.0.1:{peer}/vote",
                    json={"candidate": self.node_id}
                )

                if response.json()["vote"]:
                    votes += 1

            except:
                pass

        print(f"Votes = {votes}")

        if votes > (len(self.peers) + 1) // 2:

            self.state = "Leader"

            print(f"\n🎉 Node {self.node_id} became LEADER 🎉")

            threading.Thread(
                target=self.send_heartbeats,
                daemon=True
            ).start()

    # ---------------------------------------------------
    # Heartbeats
    # ---------------------------------------------------
    def send_heartbeats(self):

        while self.state == "Leader":

            for peer in self.peers:

                try:

                    requests.post(
                        f"http://127.0.0.1:{peer}/heartbeat"
                    )

                except:
                    pass

            print("Heartbeat Sent")

            time.sleep(2)

    # ---------------------------------------------------
    # Apply Log to State Machine
    # ---------------------------------------------------
    def apply_log(self, command):

        parts = command.split()

        if len(parts) == 4 and parts[0] == "SET":

            key = parts[1]
            value = parts[3]

            self.state_machine[key] = value

            self.last_applied = self.commit_index

            print(f"State Machine Updated : {key} = {value}")

    # ---------------------------------------------------
    # Log Replication
    # ---------------------------------------------------
    def replicate_log(self, command):

        print(f"\nClient Request : {command}")

        # Leader stores log
        self.log.append(command)

        acknowledgements = 1

        for peer in self.peers:

            try:

                response = requests.post(
                    f"http://127.0.0.1:{peer}/append",
                    json={
                        "command": command
                    }
                )

                if response.json()["success"]:

                    acknowledgements += 1

            except:
                pass

        print(f"Acknowledgements = {acknowledgements}")

        if acknowledgements > (len(self.peers) + 1) // 2:

            self.commit_index += 1

            self.apply_log(command)

            print(f"Commit Index = {self.commit_index}")

            print("✅ Log Committed")

        else:

            print("❌ Commit Failed")

    # ---------------------------------------------------
    # Run Server
    # ---------------------------------------------------
    def run(self):

        self.app.run(port=self.port)