import requests

response = requests.get("https://api.github.com/repos/shubhradeep91/devops-python-prep/pulls")
print(response.json()[0]["user"]["login"])
