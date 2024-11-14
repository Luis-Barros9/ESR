import socket
import pickle
import sys

class Node:
    def __init__(self):
        # Node name
        self.name = ''
        
        # List of neighbours
        self.neighbours = []

        # Create server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(('0.0.0.0', 6000))

        # RUN!!!
        self.get_neighbours_from_bootstrapper()

    # Define node name
    def set_node_name(self, name):
        self.name = name

    # Get neighbours from bootstrapper - TCP
    def get_neighbours_from_bootstrapper(self):
        bs_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bs_conn = socket.connect(('10.0.34.2', 5000))
        try:
            # Envia mensagem
            message = str.encode(f'NEIGHBOURS {self.name}')
            bs_conn.send(message)

            # Recebe lista de vizinhos
            self.pops = pickle.loads(bs_conn.recv(2048))
            print('Vizinhos obtidos com sucesso.')
        except:
            print('Bootstrapper offline.')
        finally:
            bs_conn.close()

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: oNode.py <node_name>")
        sys.exit(1)

    node = Node()
    node.set_node_name(sys.argv[1])
