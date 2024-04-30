# from pymilvus import connections, Collection, utility, FieldSchema, DataType, CollectionSchema

# # Connect to the Milvus service
# connections.connect("default", host="milvus-standalone", port="19530")   #host="milvus-standalone"

# # Define the schema for the collection
# schema = CollectionSchema(
#     fields=[
#         FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
#         FieldSchema(name="vec", dtype=DataType.FLOAT_VECTOR, dim=128),
#     ],
#     description="example collection"
# )

# # Create a new collection
# collection = Collection("test", schema=schema)

# # Insert some data into the collection
# data = [{"vec": [1]*128}, {"vec": [2]*128}]
# collection.insert(data)

# # Flush the data to ensure it's written to the database
# collection.flush()

# # Create an index for the collection
# index_params = {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}}
# collection.create_index("vec", index_params)

# # Load the collection
# collection.load()

# # Search the collection for vectors that are similar to [1]*128
# results = collection.search([[1]*128], "vec", limit=16000, param={"nprobe": 10})

# # Print the results
# for result in results:
#     print(result)

# # Disconnect from the Milvus service
# connections.disconnect("default")