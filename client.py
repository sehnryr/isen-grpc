import grpc
import argparse
import key_value_store_pb2
import key_value_store_pb2_grpc

def store_value(stub, key, value):
    # Create the request message for storing a key-value pair
    store_request = key_value_store_pb2.StoreRequest(key=key, value=value)
    # Send the request to the server
    store_response = stub.Store(store_request)

    # Check if the response contains an Ok message (success)
    if store_response.HasField('ok'):
        print(f"Successfully stored key: {store_response.ok.key}")
    else:
        print(f"Store Error: {store_response.error.message}")

def retrieve_value(stub, key):
    # Create the request message for retrieving a value by key
    retrieve_request = key_value_store_pb2.RetrieveRequest(key=key)
    # Send the request to the server
    retrieve_response = stub.Retrieve(retrieve_request)

    # Check if the response contains a Value (successful retrieval)
    if retrieve_response.HasField('value'):
        print(f"Retrieved key: {retrieve_response.value.key}, value: {retrieve_response.value.value}")
    else:
        print(f"Retrieve Error: {retrieve_response.error.message}")

def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Key-Value Store Client")

    # Add CLI arguments for store or retrieve
    parser.add_argument('--store', nargs=2, metavar=('key', 'value'), help="Store a key-value pair")
    parser.add_argument('--retrieve', metavar='key', help="Retrieve a value by key")

    # Parse the arguments
    args = parser.parse_args()

    # Connect to the gRPC server
    channel = grpc.insecure_channel('localhost:50051')
    stub = key_value_store_pb2_grpc.KeyValueStoreStub(channel)

    # Determine the action based on CLI arguments
    if args.store:
        # Store the key-value pair
        key, value = args.store
        store_value(stub, key, value)
    elif args.retrieve:
        # Retrieve the value for the specified key
        key = args.retrieve
        retrieve_value(stub, key)
    else:
        print("Please provide either --store <key> <value> or --retrieve <key>.")

if __name__ == '__main__':
    main()
