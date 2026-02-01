import requests

url = "http://localhost:5000/api/analyze_subscriptions"
data = {"user_id": "demo_user"}
response = requests.post(url, json=data)
print("Status Code:", response.status_code)
print("Response:", response.json())
