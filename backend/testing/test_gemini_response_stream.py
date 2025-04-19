import requests
import json

health_url = "http://localhost:5000/health"

print(requests.get(url=health_url).json())

# Define the URL and payload
url = "http://localhost:5000/rag/query"
# Send the POST request
response = requests.post(url, json={"query": "Tell me some interesting facts about airbus a380. Articulate it as if you are an avgeek"}, stream=True)

# Process the streamed response
if response.status_code == 200:
    for line in response.iter_lines():
        if line:
            data: str = json.loads(line.decode('utf-8'))
            print(data["text"], end="")
else:
    print("Error:", response.status_code)