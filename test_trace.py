import requests
import json

url = "http://127.0.0.1:8000/graph-trace"
data = {
    "text": "This system uses Credit Scoring AI for profiling."
}
try:
    response = requests.post(url, json=data)
    print(response.status_code)
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(e)
