import requests

leader_port = 5001      # Change this to the elected leader's port

response = requests.post(
    f"http://127.0.0.1:{leader_port}/client",
    json={
        "command":"SET X = 100"
    }
)

print(response.json())