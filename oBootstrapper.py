import socket
import pickle
import threading

# Map with neighbours
neighbours = {
    'n3': [ '10.0.5.2', '10.0.3.2',  '10.0.4.2'],
    'n4': ['10.0.18.2', '10.0.2.1'],
    'n5': [ '10.0.5.1', '10.0.7.2'],
    'n22': [ '10.0.3.1', '10.0.18.1', '10.0.13.2', '10.0.6.2'],
    'n7': [ '10.0.2.2', '10.0.4.1',  '10.0.8.2'],
    'n8': [ '10.0.7.1', '10.0.13.1', '10.0.11.2','10.0.12.2'],
    'n9': [ '10.0.8.1', '10.0.6.1',  '10.0.9.2', '10.0.10.2'],
    'n10': ['10.0.11.1', '10.0.27.2'],
    'n11': ['10.0.12.1', '10.0.9.1',  '10.0.26.2','10.0.24.2'],
    'n12': ['10.0.10.1', '10.0.14.2']
}

# List of points of presence
pops = ['', '', '', '']

class Bootstrapper:
    def __init__(self):
        # Create socket
        bootstrapper = socket.socket()
        bootstrapper.bind(('0.0.0.0', 5000))

        print('Bootstrapper listening for connections!')
        try:
            while True:
                bootstrapper.listen()
                conn, addr = bootstrapper.accept()
                threading.Thread(target= self.handler, args=(conn, addr)).start()
        finally:
            bootstrapper.close()

    # Bootstrapper connection handler
    def handler(self, connection, address):
        ip = str(address[0])
        print(f"[INFO] {ip} connection started.")
        data = connection.recv(1024).decode('utf-8')
        if data.startswith('NEIGHBOURS'):
            _, node_id = data.split()
            if node_id in neighbours:
                response = pickle.dumps(neighbours[node_id])
            else:
                response = pickle.dumps({"error": "Invalid node id"})
        elif data.startswith('POPS'):
            response = pickle.dumps(pops)
        else:
            response = pickle.dumps({"error": "Invalid command"})
        connection.send(response)
        print(f"[INFO] Neighbours sent for {node_id}.")
        connection.close()
        print(f"[INFO] {ip} connection closed.")

if __name__ == "__main__":
    bootstrapper = Bootstrapper()