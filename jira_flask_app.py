from flask import Flask, request
import requests
from requests.auth import HTTPBasicAuth
import json
import os

app = Flask(__name__)

@app.route("/createJIRA", methods=["POST"])
def createJIRA():

    webhook_payload = request.get_json()
    comment_body = webhook_payload.get('comment', {}).get('body')

    if comment_body == '/jira':
        url = "https://shubhradeep91.atlassian.net/rest/api/3/issue"

        auth = HTTPBasicAuth("shubhradeep.ghatak@gmail.com", os.getenv("JIRA_API_TOKEN"))

        headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
        }

        payload = json.dumps( {
        "fields": {
            "description": {
            "content": [
                {
                "content": [
                    {
                    "text": "My first Jira Ticket",
                    "type": "text"
                    }
                ],
                "type": "paragraph"
                }
            ],
            "type": "doc",
            "version": 1
            },
            "issuetype": {
            "id": "10003"
            },
            "project": {
            "key": "SG"
            },
            "summary": "First JIRA Ticket with Flask app",
        },
        "update": {}
        } )

        response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
        auth=auth
        )

        return json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
    
    else:
        print(f"Webhook received, but comment was '{comment_body}'. No Jira ticket created.")
        return json.dumps({"status": "ignored", "message": "Comment did not match '/jira'."}), 200


if __name__ == '__main__':
    app.run("0.0.0.0")