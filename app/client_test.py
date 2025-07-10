from app.conn.weaviate_client import WeaviateClient

print("Trying to connect to weaviate...")
weaviate_wrapper = WeaviateClient()
weaviate_wrapper.init_client()
print("Closing the connection")
weaviate_wrapper.close()