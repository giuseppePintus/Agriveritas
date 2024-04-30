from pymilvus import connections, Collection, FieldSchema, DataType, CollectionSchema

# Connect to the Milvus service
connections.connect("default", host="milvus-standalone", port="19530")

# Assuming you have created a collection named "test"
collection = Collection("test")

# Drop the collection
collection.drop()

# Disconnect from the Milvus service
connections.disconnect("default")