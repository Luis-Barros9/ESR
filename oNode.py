import socket
import threading
import pickle
import sys

class Node:
    def __init__(self):
        # List of neighbours
        self.neighbours = []

        # Create server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(('0.0.0.0', 6000))

        # RUN!!!
        self.get_neighbours_from_bootstrapper()

    # Get neighbours from bootstrapper - TCP
    def get_neighbours_from_bootstrapper(self):
        BOOTSTRAPPER_IP = '10.0.34.2'
        BOOTSTRAPPER_PORT = 5000
        try:
            print("[INFO] Connecting with bootstrapper...")
            bs_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            bs_conn.connect((BOOTSTRAPPER_IP, BOOTSTRAPPER_PORT))
            print("[INFO] Requesting neighbours from bootstrapper...")
            message = f"NEIGHBOURS {sys.argv[1]}"
            bs_conn.send(message.encode('utf-8'))
            response = bs_conn.recv(4096)
            self.neighbours = pickle.loads(response)
            print(f"[INFO] Neighbours received from bootstrapper: {self.neighbours}")
        except Exception as e:
            print(f"[ERROR] Failed to retrieve neighbours from bootstrapper: {e}")

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: oNode.py <node_name>")
        sys.exit(1)

    node = Node()