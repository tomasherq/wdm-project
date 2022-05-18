import requests
from common.tools import *
from flask import Flask, request
import sys
import os

app = Flask("order-service")

# Each one of the services will run an instance, run in a different port and have different clients

# I want to have the address and port of the clients.
clientsDirections = ["http://192.168.124.10:2801"]


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['POST', 'GET', 'DELETE'])
def catch_all(path):
    print(path)
    responses = []
    for clientDir in clientsDirections:
        url = f"{clientDir}/{path}"

        if request.method == 'POST':
            reply = json.loads(requests.post(url).text)
        elif request.method == "GET":
            reply = json.loads(requests.get(url).text)
        elif request.method == "DELETE":
            reply = json.loads(requests.delete(url).text)
        else:
            return response(401, f"Used invalid method")

        responses.append(reply)

    if all(reply == responses[0] for reply in responses):
        return responses[0]
    else:
        return response(501, f"Server error occured")


app.run(host="192.168.124.11", port=2802)

