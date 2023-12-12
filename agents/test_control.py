import json
import requests

glb_payload = {
  "f1":{
    "policy": {
        "f1-r1": 1,
        "f1-r2": 9,
        "f1-r3": 3
    }
  }
}

glb_url = 'http://localhost:8080/policy'

def send_data(url, payload, headers={'Content-Type': 'application/json'}):
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print('sent ')
    print(response.text)


send_data(url=glb_url,payload=glb_payload)