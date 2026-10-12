import requests
url = "http://127.0.0.1:5001/vote"


data = {
    "candidate": 1
}

response = requests.post(url, json=data)

print(response.json())