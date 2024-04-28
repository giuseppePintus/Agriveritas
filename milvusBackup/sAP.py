

from pymilvus import connections

print("\n @@@@@@ B @@@@@@ \n")

#Check if Milvus has connection to the server
print(connections.has_connection("default"))

#List all connections
print("\n @@@@@@ C @@@@@@ \n")
print(connections.list_connections())

#Remove connection from Milvus
connections.remove_connection("default")

print("\n @@@@@@ D @@@@@@ \n")
print(connections.list_connections())