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
import time

# test if sync works

# PASSWORD = os.environ.get('MONGO_PASSWORD')
PREFIX_IP = os.environ.get("PREFIX_IP")
ID_NODE = int(sys.argv[1])
RECOVERY_RESPONSE = "In recovery mode."

# Maybe we should check if the reply from Mongo is successful?
# Or we could not notify the user, just enqueue. Will be succesful until queried again

# Extra feature that can be used for consistency.


class CollectionWrapperMongo():
    '''The pourpose of this function is enabiling logging of the information.
    '''

    def __init__(self, collection, service, logging=False):
        self.collection = collection
        self.log_file_name = f"/var/log/{service}-{ID_NODE}.ndjson"
        self.logging = logging
        self.recovery_mode = False
        self.request_queue = list()

    def log_request(self, information):

        if self.logging is True:

            with open(self.log_file_name, "a") as file:
                file.write(json.dumps(information))
                file.write("\n")

    def enqueue(self, request_object):
        self.request_queue.append(request_object)

    def is_queue_empty(self):
        return len(self.request_queue) == 0

    def process_queue(self):

        # This will execute the recovery
        if not self.is_queue_empty():
            while len(self.request_queue) > 0:
                request_to_process = self.request_queue.pop(0)

                request_type = request_to_process["request_type"]
                try:
                    if request_type == "update_object":
                        self.collection.update_one(request_to_process["update_id"], request_to_process["newvalues"])
                    elif request_type == "insert":
                        self.collection.insert_one(request_to_process["object"])
                    elif request_type == "delete":
                        self.collection.delete_one(request_to_process["object"])
                except Exception as e:
                    # If we find an error we notify it
                    self.request_queue.append(request_to_process)
                    return str(e)
        # This is so that the return is homogeneous
        self.recovery_mode = False
        return "Success"

    def update_one(self, update_object, newvalues):

        request_object = {"request_type": "update_object", "update_id": update_object, "newvalues": newvalues}

        if self.recovery_mode:
            self.enqueue(request_object)
            return RECOVERY_RESPONSE

        self.log_request(request_object)

        return self.collection.update_one(update_object, newvalues)

    def insert_one(self, insert_object):

        insert_object["timestamp"] = float(insert_object["timestamp"])
        request_object = {"request_type": "insert", "object": insert_object}
        if self.recovery_mode:
            self.enqueue(request_object)
            return RECOVERY_RESPONSE

        self.log_request(request_object)
        return self.collection.insert_one(insert_object)

    def delete_one(self, delete_object):

        request_object = {"request_type": "delete", "object": delete_object}

        if self.recovery_mode:
            self.enqueue(request_object)
            return RECOVERY_RESPONSE

        self.log_request(request_object)
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
    response._status_code = status
    response.status_code = status

    if id_request is not None:
        response.headers["Id-request"] = id_request

    return response


def getDatabase(database_name):
    client = MongoClient("localhost", 27017)
    return client[database_name]


def getCollection(database, collection_name):

    return CollectionWrapperMongo(database[collection_name], collection_name)


def getAmountOfItems(collection):
    return len(list(collection.find({})))


def encodeBase64(string):
    encodedBytes = base64.b64encode(string.encode("utf-8"))
    return str(encodedBytes, "utf-8")


def decodeBase64(string):
    return base64.b64decode(string)


def getIPAddress(service):
    return "localhost"
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


def make_request(method, url, headers):

    try:
        return requests.request(method, url, headers=headers)
    except Exception:
        return {"status_code": 505, "message": "Invalid URL."}


def process_reply(data_reply, return_raw=False):

    if isinstance(data_reply, dict) and "status_code" in data_reply and data_reply["status_code"] == 505:
        return data_reply
    try:
        return data_reply.text if return_raw else json.loads(data_reply.text)
    except:
        return {"status_code": 501, "message": "Invalid URL."}


def debug_print(*vars):

    print(vars, file=sys.stdout, flush=True)


def is_invalid_reply(reply):
    return isinstance(reply, dict) and "status_code" in reply and reply["status_code"] == 505
