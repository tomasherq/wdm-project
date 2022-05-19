import requests
from common.tools import *
from flask import Flask, request
import sys
import os

app = Flask("order-service")

# Each one of the services will run an instance, run in a different port and have different clients

# I want to have the address and port of the clients.

serviceID = sys.argv[2]


@app.post('/request/<str:request_info>', methods=['POST'])
def catch_all(request_info):

    nodesDirections = getAddresses(f"{serviceID}_NODES_ADDRESS")
    try:
        items = json.loads(decodeBase64(request_info))
        print(items)
    except:
        return response(500, "Invalid format")

    return response(200, "Success")


app.run(host=getIPAddress(f"{serviceID}_COORD_ADDRESS"), port=2802)
