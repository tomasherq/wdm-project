import base64
from pymongo import MongoClient
import json
import os
import sys
import requests
import math
from flask import Flask, request, make_response
from hashlib import md5
from collections import defaultdict

# test if sync works

# PASSWORD = os.environ.get('MONGO_PASSWORD')
PREFIX_IP = os.environ.get("PREFIX_IP")
ID_NODE = int(sys.argv[1])


# Extra feature that can be used for consistency.
class CollectionWrapperMongo():
    '''The pourpose of this function is enabiling logging of the information.
    '''

    def __init__(self, collection, service):
        self.collection = collection
        self.log_file_name = f"/var/log/{service}-{ID_NODE}.ndjson"

    def log_request(self, information):

        with open(self.log_file_name, "a") as file:
            file.write(json.dumps(information))
            file.write("\n")

    def update_one(self, update_object, newvalues):
        self.log_request({"request_type": "update_object", "update_id": update_object, "newvalues": newvalues})
        return self.collection.update_one(update_object, newvalues)

    def insert_one(self, insert_object):
        self.log_request({"request_type": "insert", "object": insert_object})
        return self.collection.insert_one(insert_object)

    def delete_one(self, delete_object):
        self.log_request({"request_type": "delete", "object": delete_object})
        return self.collection.delete_one(delete_object)

    def find_one(self, request_object):
        return self.collection.find_one(request_object)

    def find(self, request_object):
        return self.collection.find(request_object)

    def drop(self):
        self.log_request({"request_type": "drop", "object": {}})
        return self.collection.drop()


def response(status, object, id_request=None):
    data_response = json.dumps(object)

    response = make_response(data_response, status)

    if id_request is not None:
        response.headers["Id-request"] = id_request
    return response


def getDatabase(database_name):
    client = MongoClient("localhost", 27017)
    return client[database_name]


def getCollection(database, collection_name, use_wrapper=False):

    collection = database[collection_name]
    if use_wrapper is True:
        CollectionWrapperMongo(collection, collection_name)

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


def getIdRequest(sentence):
    return str(md5(sentence.encode()).hexdigest())


def getIndexFromCheck(nNodes, md5Id):

    # LIMITATION: Same order executed will get the same Id, so it might be that a node is overloaded....
    checkNum = ''
    for i in md5Id:
        if i.isdigit():
            checkNum += i

    indexMaxNodes = nNodes-1

    if indexMaxNodes == 0:
        return 0

    nDigits = int(math.log(nNodes, 10))+1

    while len(checkNum) < nDigits:
        checkNum = checkNum+checkNum

    index = int(checkNum[:nDigits])

    while index > indexMaxNodes:
        index -= indexMaxNodes

    return index


def request_is_read(request):
    return "check_availability" in request.path or request.method == "GET" or "/status" in request.path


def process_reply(data_reply, return_raw=False):
    try:
        return data_reply.text if return_raw else json.loads(data_reply.text)
    except:
        return {"status_code": 501, "message": "Invalid URL."}


def debug_print(var):
    return print(var, file=sys.stdout, flush=True)
