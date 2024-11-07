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



if __name__ == "__main__":
    servidor = Servidor()