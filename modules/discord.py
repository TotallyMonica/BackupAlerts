import requests
import socket
import json

class Discord:
    def __init__(self, webhook):
        self.webhook = webhook

    def send(self, data):
        if data['status'] == 'starting':
            parsed_data = [{
                'name': "destination",
                'value': f'{data["remote"]}'
            },
            {
                'name': "Status",
                'value': "Starting",
                'inline': True
            }]
        elif data['status'] == 'complete':
            parsed_data = [{
                    "name": "Destination",
                    "value": f"{data['remote']}"
                },
                {
                    "name": "Successful?",
                    "value": f"{data['result'] == 0}",
                    "inline": True
                },
                {
                    "name": "Time",
                    "value": f"{data['time']}",
                    "inline": True
                }]
        content = {
            "embeds": [{
                    "title": f"{socket.gethostname()}",
                    "color": 15258703,
                    "fields": parsed_data
                }
            ]
        }

        try:
            req = requests.post(self.webhook, data=json.dumps(content), headers={'Content-type': 'application/json'})
            req.raise_for_status()
            print(f"Message sent successfully.")
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            print(f"Request Exception: {err}")