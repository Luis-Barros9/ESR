import socket
import threading
import pickle
import netifaces
import sys

PORT = 5000  # Define a single, fixed port for all oNode instances
BOOTSTRAPPER_IP = '10.0.34.2'  # IP of the bootstrapper

class ONode:
    def __init__(self):
        self.neighbors = []  # Initialize an empty neighbors list
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = sys.argv[1] # Node name -- Important to distinguish this node from others

        # Allow reuse of the same address
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to the fixed port
        self.server_socket.bind(('0.0.0.0', PORT))
        self.server_socket.listen(5)
        print(f"[INFO] oNode running on port {PORT}, waiting for connections...")

        # Track active connections
        self.connections = {}  # Dictionary to store connections with each neighbor

        # Request neighbors from bootstrapper at startup
        self.get_neighbors_from_bootstrapper()

    def get_neighbors_from_bootstrapper(self):
        # for each interface, get the IP address
        for interface in netifaces.interfaces():
            if interface == "lo":
                continue
            iface = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
            if iface is not None:
                node_ip = iface[0]['addr']
                print(f"[INFO] Node IP: {node_ip}")

                # Connect to bootstrapper to request neighbors for each IP
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as bootstrapper_socket:
                    try:
                        bootstrapper_socket.connect((BOOTSTRAPPER_IP, PORT))
                        print("[INFO] Connected to bootstrapper")
                        message = f"NEIGHBOURS {self.name}"  # Request neighbors for this node's IP
                        print("[INFO] Requesting neighbors from bootstrapper...")
                        bootstrapper_socket.send(message.encode('utf-8'))
                        # Receive the list of neighbors from bootstrapper
                        response = bootstrapper_socket.recv(4096)
                        neighbors_for_ip = pickle.loads(response)
                        if "error" in neighbors_for_ip:
                            continue # Skip this IP if an error occurred -> this happens for neighbours in the underlay that are not neighbors in the overlay
                        else:
                            self.neighbors.append(neighbors_for_ip) 
                            print(f"[INFO] Neighbors received from bootstrapper for {node_ip}: {neighbors_for_ip}")
                    except Exception as e:
                        print(f"[ERROR] Failed to retrieve neighbors from bootstrapper: {e}")

    def handle_client(self, client_socket, addr):
        print(f"[INFO] Connection established with {addr}")
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"[MESSAGE] Received from {addr}: {message}")
        except ConnectionResetError:
            print(f"[INFO] Connection reset by {addr}")
        finally:
            client_socket.close()
            print(f"[INFO] Connection closed with {addr}")

    def listen_for_connections(self):
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                client_handler.start()
            except Exception as e:
                print(f"[ERROR] Accepting connection: {e}")

    def connect_to_neighbors(self):
        for neighbor in self.neighbors:
            if neighbor not in self.connections:  # Avoid reconnecting if already connected
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((neighbor, PORT))
                    print(f"[INFO] Connected to neighbor {neighbor}")
                    client_socket.send("HELLO".encode('utf-8'))  # Initial hello message
                    self.connections[neighbor] = client_socket  # Track active connection
                    
                    # Start a thread to listen for responses from this neighbor
                    threading.Thread(target=self.listen_to_neighbor, args=(client_socket, neighbor)).start()
                except Exception as e:
                    print(f"[ERROR] Could not connect to {neighbor}: {e}")

    def listen_to_neighbor(self, client_socket, neighbor):
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"[MESSAGE] Received from {neighbor}: {message}")
        except ConnectionResetError:
            print(f"[INFO] Connection reset by {neighbor}")
        finally:
            client_socket.close()
            print(f"[INFO] Connection to {neighbor} closed")
            del self.connections[neighbor]  # Remove from active connections

    def start(self):
        threading.Thread(target=self.listen_for_connections).start()
        self.connect_to_neighbors()

if __name__ == "__main__":
    node = ONode()
    # Checking if the neighbors are correctly fetched
    print("------------")
    print(node.neighbors)
    # Start the oNode
    node.start()