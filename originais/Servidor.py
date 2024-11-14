import sys
import socket
import json
# Lista com POPs
pops = ['10.0.27.1',
        '10.0.26.1',
        '10.0.24.1',
        '10.0.14.1']

class Servidor:
    def __init__(self):
        # Configurações do servidor
        self.SERVER_PORT = 6000
        self.SERVER_HOST = '0.0.0.0'  # Permite conexões de qualquer IP
        self.server_socket = None
        self.neighboors= {}
        # Criação do socket do servidor
        self.create_socket()

    def create_socket(self):
        try:
            # Inicializa o socket do servidor como UDP
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind((self.SERVER_HOST, self.SERVER_PORT))
            print(f"Servidor iniciado e escutando na porta {self.SERVER_PORT}")
        except Exception as e:
            print(f"Erro ao configurar o socket do servidor: {e}")
            sys.exit(1)
    
    
    def get_neighbors_from_bootstrapper(self):
        # Connect to bootstrapper to request neighbors for each IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as bootstrapper_socket:
            try:
                bootstrapper_socket.connect((BOOTSTRAPPER_IP, PORT))
                print("[INFO] Connected to bootstrapper")
                message = "NEIGHBOURS servidor"  # Request neighbors for this node
                print("[INFO] Requesting neighbors from bootstrapper...")
                bootstrapper_socket.send(message.encode('utf-8'))
                # Receive the list of neighbors from bootstrapper
                response = bootstrapper_socket.recv(4096)
                neighbors_for_ip = pickle.loads(response)
                for n in neighbors_for_ip:
                    self.neighbors[n]= False
                print(f"[INFO] Neighbors received from bootstrapper: {neighbors_for_ip}")
            
            except Exception as e:
                print(f"[ERROR] Failed to retrieve neighbors from bootstrapper: {e}")



if __name__ == "__main__":
    servidor = Servidor()