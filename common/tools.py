import base64
from pymongo import MongoClient
import json
import os
import sys
import requests
import math
from flask import Flask, request
from ipv4checksum import checksum
# test if sync works
PASSWORD = os.environ.get('MONGO_PASSWORD')
PREFIX_IP = os.environ.get("PREFIX_IP")
ID_NODE = int(sys.argv[1])

# test if sync works from pc to container


def response(code, text):
    return json.dumps({"status": code, "message": text})


def getCollection(database, collection):
    client = MongoClient("mongodb+srv://user:" + PASSWORD +
                         "@gala.iykme.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", 27017)
    # client = MongoClient("localhost", 27017)
    database = client[database]
    collection = database[collection]

    return collection


def getAmountOfItems(collection):
    return len(list(collection.find({})))


def encodeBase64(string):
    encodedBytes = base64.b64encode(string.encode("utf-8"))
    return str(encodedBytes, "utf-8")


def decodeBase64(string):
    return base64.b64decode(string)


def getIPAddress(service):

    return PREFIX_IP+"."+os.environ.get(service).split(";")[ID_NODE-1]


def getAddresses(service, port=2801):
    addresses = list()
    for address in os.environ.get(service).split(";"):
        addresses.append(f'http://{PREFIX_IP}.{address}:{port}')
    return addresses


def getIndexFromCheck(nNodes, checkNum):
    indexMaxNodes = nNodes-1

    if indexMaxNodes == 0:
        return 0

    nDigits = int(math.log(nNodes, 10))+1

    checkNum = str(checkNum)

    while len(checkNum) < nDigits:
        checkNum = checkNum+checkNum

    index = int(str(checkNum)[:nDigits])
    while index > indexMaxNodes:
        index -= indexMaxNodes

    return index


def sendMessageCoordinator(info, coordinators):
    json_info = json.dumps(info)

    idInfo = checksum(json_info)
    info["id"] = idInfo
    infoEncoded = encodeBase64(json.dumps(info))
    coordinatorAddress = coordinators[getIndexFromCheck(len(coordinators), idInfo)]

    url = f'{coordinatorAddress}/{infoEncoded}'

    return requests.post(url)


def checkAccess(request, allowedAddresses):
    return request.remote_addr in allowedAddresses
