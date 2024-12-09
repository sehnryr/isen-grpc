import grpc
import click
import time
import key_value_store_pb2
import key_value_store_pb2_grpc
from pymongo import MongoClient
from concurrent import futures
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

class KeyValueStoreServicer(key_value_store_pb2_grpc.KeyValueStoreServicer):
    def __init__(self):
        # Get MongoDB environment variables
        mongo_db = os.getenv("MONGODB_ADDON_DB")
        mongo_uri = os.getenv("MONGODB_ADDON_URI")

        if not mongo_uri:
            raise ValueError("MONGO_URI is not set in the .env file")

        # Connect to MongoDB
        self.client = MongoClient(mongo_uri)
        self.db = self.client[mongo_db]  # Database name
        self.collection = self.db["store"]  # Collection name

    def Store(self, request, context):
        # Store the key-value pair
        key = request.key
        value = request.value

        # Check if the key already exists in the database
        existing_entry = self.collection.find_one({"key": key})

        if existing_entry:
            # Update the existing entry
            self.collection.update_one({"key": key}, {"$set": {"value": value}})
            print(f"Updated key: {key} with new value: {value}")
        else:
            # Insert a new key-value pair
            self.collection.insert_one({"key": key, "value": value})
            print(f"Stored new key: {key} with value: {value}")

        # Return the successful response
        return key_value_store_pb2.StoreResponse(ok=key_value_store_pb2.Ok(key=key))

    def Retrieve(self, request, context):
        # Retrieve the value by key
        key = request.key

        # Search for the key in the MongoDB collection
        result = self.collection.find_one({"key": key})

        if result:
            # Return the value if found
            return key_value_store_pb2.RetrieveResponse(
                value=key_value_store_pb2.Value(key=result["key"], value=result["value"])
            )
        else:
            # Return an error if the key is not found
            return key_value_store_pb2.RetrieveResponse(
                error=key_value_store_pb2.Error(message="Key not found")
            )

# CLI command to start the server
@click.command()
@click.option('--port', default=50051, type=int, help="Port for the server to listen on.")
@click.option('--workers', default=10, type=int, help="Number of worker threads to handle requests.")
def serve(port, workers):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))
    key_value_store_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStoreServicer(), server)

    server.add_insecure_port(f'[::]:{port}')
    print(f"Server starting on port {port} with {workers} workers...")
    server.start()

    # Waiting for termination signals (Ctrl+C)
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
