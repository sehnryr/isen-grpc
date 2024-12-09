import grpc
import click
import key_value_store_pb2
import key_value_store_pb2_grpc

def store_value(stub, key, value):
    # Create the request message for storing a key-value pair
    store_request = key_value_store_pb2.StoreRequest(key=key, value=value)
    # Send the request to the server
    store_response = stub.Store(store_request)

    # Check if the response contains an Ok message (success)
    if store_response.HasField('ok'):
        click.echo(f"Successfully stored key: {store_response.ok.key}")
    else:
        click.echo(f"Store Error: {store_response.error.message}")

def retrieve_value(stub, key):
    # Create the request message for retrieving a value by key
    retrieve_request = key_value_store_pb2.RetrieveRequest(key=key)
    # Send the request to the server
    retrieve_response = stub.Retrieve(retrieve_request)

    # Check if the response contains a Value (successful retrieval)
    if retrieve_response.HasField('value'):
        click.echo(f"Retrieved key: {retrieve_response.value.key}, value: {retrieve_response.value.value}")
    else:
        click.echo(f"Retrieve Error: {retrieve_response.error.message}")

# Main Click command to interact with the client
@click.command()
@click.option('--port', default=50051, type=int, help="Port for the server to listen on.")
@click.option('--store', nargs=2, metavar=('key', 'value'), help="Store a key-value pair")
@click.option('--retrieve', metavar='key', help="Retrieve a value by key")
def main(port, store, retrieve):
    # Connect to the gRPC server
    channel = grpc.insecure_channel(f'[::]:{port}')
    stub = key_value_store_pb2_grpc.KeyValueStoreStub(channel)

    if store:
        key, value = store
        store_value(stub, key, value)
    elif retrieve:
        key = retrieve
        retrieve_value(stub, key)
    else:
        click.echo("Please provide either --store <key> <value> or --retrieve <key>.")

if __name__ == '__main__':
    main()
