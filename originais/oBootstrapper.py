import socket
import pickle
import threading

# Map with neighbours
neighbours = {
    'servidor': ['10.0.0.1', '10.0.1.1', '10.0.2.1'],
    'n2': ['10.0.0.10', '10.0.4.2', '10.0.8.1'],
    'n4': ['10.0.2.10', '10.0.21.2', '10.0.5.1'],
    'n22': ['10.0.6.2', '10.0.7.2', '10.0.4.1'],
    'n6': ['10.0.12.2', '10.0.14.2', '10.0.23.2', '10.0.3.2', '10.0.21.1'],
    'n7': ['10.0.22.2', '10.0.13.2', '10.0.5.2'],
    'n8': ['10.0.16.2', '10.0.6.1', '10.0.11.1'],
    'n9': ['10.0.17.2', '10.0.18.2', '10.0.15.2', '10.0.7.1', '10.0.10.1', '10.0.12.1'],
    'n10': ['10.0.24.2', '10.0.16.1', '10.0.17.1'],
    'n11': ['10.0.26.2', '10.0.27.2', '10.0.15.1', '10.0.14.1'],
    'n12': ['10.0.29.2', '10.0.13.1'],
}

# Host and port configuration
HOST = '0.0.0.0'
PORT = 5000

# Create socket
server = socket.socket()
server.bind((HOST, PORT))

# Server connection handler
def handler(connection, address):
    ip = str(address[0])
    print(f"{ip} - Connection established.")
    
    try:
        # Receive the data from the client
        data = connection.recv(1024).decode('utf-8')
        print(f"Received: {data}")
        if data.startswith("NEIGHBOURS"):
            _, node_id = data.split()
            # Fetch neighbours
            if node_id in neighbours:
                response = pickle.dumps(neighbours[node_id])
            else:
                response = pickle.dumps({"error": "Node not found"})
                
        else:
            response = pickle.dumps({"error": "Invalid command"})
        
        # Send response to the client
        connection.send(response)
        print(f"Neighbours sent for {node_id}.")
        
    except Exception as e:
        print(f"Error handling request from {ip}: {e}")
        connection.send(pickle.dumps({"error": str(e)}))
        
    finally:
        connection.close()
        print(f"{ip} - Connection closed.")

# Server listening for new connections
print('Bootstrapper listening for new connections! =)')
while True:
    server.listen()
    conn, addr = server.accept()
    threading.Thread(target=handler, args=(conn, addr)).start()
