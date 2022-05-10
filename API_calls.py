from pymongo import MongoClient

myclient = MongoClient('localhost', 27017)

# Select the database to be used
mydb = myclient["database_test"]

# Select the collection to be created
mycol = mydb["customers"]

# Things to be inserted
mydict = {"name": "John", "address": "Highway 37"}

# Insert one
x = mycol.insert_one(mydict)


# Insert many
mylist = [
    {"name": "Amy", "address": "Apple st 652"},
    {"name": "Hannah", "address": "Mountain 21"},
    {"name": "Michael", "address": "Valley 345"},
    {"name": "Sandy", "address": "Ocean blvd 2"},
    {"name": "Betty", "address": "Green Grass 1"},
    {"name": "Richard", "address": "Sky st 331"},
    {"name": "Susan", "address": "One way 98"},
    {"name": "Vicky", "address": "Yellow Garden 2"},
    {"name": "Ben", "address": "Park Lane 38"},
    {"name": "William", "address": "Central st 954"},
    {"name": "Chuck", "address": "Main Road 989"},
    {"name": "Viola", "address": "Sideway 1633"}
]

x = mycol.insert_many(mylist)

# Print the stuff
# print(x.inserted_id)
# This includes only the fields with value 1 and excludes the ones with value 0
for x in mycol.find({}, {"_id": 0, "name": 1, "address": 1}):
    print(x)


# Query for a document with an attribute
myquery = {"address": "Park Lane 38"}

mydoc = mycol.find(myquery)

for x in mydoc:
    print(x)


# Advanced query

myquery = {"address": {"$gt": "S"}}

mydoc = mycol.find(myquery)

for x in mydoc:
    print(x)

# With regex query
myquery = {"address": {"$regex": "^S"}}

# We can sort the obtained results easily, -1 is descending order
mydoc = mycol.find(myquery).sort("name", -1)

for x in mydoc:
    print(x)

# In order to delete documents
myquery = {"address": "Mountain 21"}

mycol.delete_one(myquery)

# Delete many
myquery = {"address": {"$regex": "^S"}}

x = mycol.delete_many(myquery)
# Delete all
x = mycol.delete_many({})

# Drop collection
mycol.drop()

# Update one
myquery = {"address": "Valley 345"}
newvalues = {"$set": {"address": "Canyon 123"}}

mycol.update_one(myquery, newvalues)


# Update many
myquery = {"address": {"$regex": "^S"}}
newvalues = {"$set": {"name": "Minnie"}}

x = mycol.update_many(myquery, newvalues)

# Limit retrieved results

myresult = mycol.find().limit(5)


print(myclient.list_database_names())
print(mydb.list_collection_names())
