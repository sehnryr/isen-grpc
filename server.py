import grpc
from concurrent import futures
import time
import key_value_store_pb2
import key_value_store_pb2_grpc

class KeyValueStoreServicer(key_value_store_pb2_grpc.KeyValueStoreServicer):
    def __init__(self):
        # Initialize an in-memory dictionary to store key-value pairs
        self.store = {}

    def Store(self, request, context):
        # Store the key-value pair
        key = request.key
        value = request.value
        self.store[key] = value
        # Return a successful response
        return key_value_store_pb2.StoreResponse(ok=key_value_store_pb2.Ok(key=key))

    def Retrieve(self, request, context):
        # Retrieve the value by key
        key = request.key
        if key in self.store:
            # Return the value for the given key
            return key_value_store_pb2.RetrieveResponse(value=key_value_store_pb2.Value(key=key, value=self.store[key]))
        else:
            # Return an error if the key is not found
            return key_value_store_pb2.RetrieveResponse(error=key_value_store_pb2.Error(message="Key not found"))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    key_value_store_pb2_grpc.add_KeyValueStoreServicer_to_server(KeyValueStoreServicer(), server)

    server.add_insecure_port('[::]:50051')
    print("Server starting on port 50051...")
    server.start()

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
