import requests
import json

class HomeAssistant:
    def __init__(self, token, url):
        if token:
            self.token = token
        else:
            raise Exception("Error: Token is missing for the Home Assistant integration")

        if url and url.lower().startswith("http://") or url.lower().startswith("https://"):
            if url[-1] == '/':
                self.url = url[:-1]
            else:
                self.url = url
        else:
            raise Exception("Error: URL is missing for the Home Assistant integration or is incorrectly formatted")

    def send(self, data):
        # Create the headers needed for the server
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'
        }

        # Format received data to a format friendly to HASS
        parsed_data = {
            "title": f"Backup from {data['source']} to {data['remote']}"
        }

        # Prompt for if it is starting
        if data['status'] == 'starting':
            parsed_data["message"] = f"Backup from {data['source']} to {data['remote']} is beginning"

        elif data['status'] == 'complete':
            alert_body = f"Backup from {data['source']} to {data['remote']} has [[result]] in {data['time']}"
            if data['result'] == 0:
                parsed_data["message"] = alert_body.replace("[[result]]", "completed successfully")
            else:
                parsed_data["message"] = alert_body.replace("[[result]]", f"errored with status code {data['result']}")

        # POST to the endpoint
        r = requests.post(self.url + "/api/services/notify/notify", headers=headers, data=json.dumps(parsed_data))
        if r.status_code != 200:
            print("Error sending to Home Assistant instance")
        print(r.status_code)
        print(r.text)
