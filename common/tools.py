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
# test if sync works from pc to container


def response(code, text):
    return json.dumps({"status": code, "message": text})


def getCollection(database, collection):
    client = MongoClient("mongodb+srv://user:" + PASSWORD +
                         "@gala.iykme.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", 27017)
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
    ID_NODE = int(sys.argv[1])-1

    return PREFIX_IP+"."+os.environ.get(service).split(";")[ID_NODE]


def getAddresses(service):
    addresses = list()
    for address in +os.environ.get(service).split(";"):
        addresses.append(f'http://{PREFIX_IP}.{address}:2801')
    return addresses


def getIndexFromCheck(nNodes, numberCheck):

    if nNodes == 1:
        return 1

    nDigits = int(math.log(nNodes, 10))+1

    numberCheck = str(numberCheck)

    while len(numberCheck) < nDigits:
        numberCheck = numberCheck+numberCheck

    number = int(str(numberCheck)[:nDigits])
    while number > nNodes:
        number -= nNodes

    return number


def sendMessageCoordinator(info, coordinators):
    json_info = json.dumps(info)

    idInfo = checksum(json_info)
    info["id"] = idInfo
    infoEncoded = encodeBase64(json.dumps(info))
    coordinatorIP = coordinators[getIndexFromCheck(len(coordinators), idInfo)]
    url = f'http://{coordinatorIP}:2802/{infoEncoded}'

    return requests.post(url)


def checkAccess(request, allowedAddresses):
    return request.remote_addr in allowedAddresses
