from pymilvus import MilvusClient

# Connect to Milvus
client = MilvusClient(uri="http://milvus-standalone:19530")

# Load the collection and partition
collection_name = "chunk"
partition_name = "ER1PSR"

print(client.list_collections())

client.load_collection(collection_name, partition_names=[partition_name])


results = client.get(
    collection_name="quick_setup",
    ids=["ER1PSR_0_0"],
    partition_names=[partition_name]
)
# # Prepare the search parameters
# search_params = {
#     "metric_type": "L2",  # or "IP" for inner product, depending on your vector index
#     "params": {"nprobe": 10},  # adjust based on your needs
# }

# # Define the field to search on and the query
# vector_field = "vector"  # replace with your actual vector field name
# query_vector = [...]  # replace with your actual query vector

# # Perform the search
# results = client.search(
#     collection_name=collection_name,
#     data=[query_vector],
#     anns_field=vector_field,
#     param=search_params,
#     limit=10,  # number of results to return
#     expr='ID_univoco == "ER1PSR_0_0"',
#     output_fields=["ID_univoco", "your_other_fields"],  # fields to return in results
#     partition_names=[partition_name]
# )

# Process the results
for hit in results[0]:
    print(f"ID: {hit.id}, Distance: {hit.distance}, ID_univoco: {hit.entity.get('ID_univoco')}")

# Remember to release the collection when done
client.release_collection(collection_name)