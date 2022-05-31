import base64
from pymongo import MongoClient
import json
import os
import sys
import requests
import math
from flask import Flask, request
from hashlib import md5

# test if sync works

# PASSWORD = os.environ.get('MONGO_PASSWORD')
PREFIX_IP = os.environ.get("PREFIX_IP")
ID_NODE = int(sys.argv[1])

# test if sync works from pc to container


def response(code, text):
    return json.dumps({"status": code, "message": text})


def getDatabase(database_name):

    client = MongoClient("localhost", 27017)

    return client[database_name]


def getCollection(database, collection_name):

    return database[collection_name]


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


def checksum(sentence):
    result = md5(sentence.encode()).hexdigest()
    check = ''
    for i in result:
        if i.isdigit():
            check += i
    return int(check)


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
