import sys
import socket
import threading

# Lista com POPs
pops = ['10.0.27.1', '10.0.26.1', '10.0.24.1', '10.0.14.1']

class Servidor:
    def __init__(self):
        # Configurações do servidor
        self.SERVER_PORT = 6000
        self.SERVER_HOST = '0.0.0.0'  # Permite conexões de qualquer IP
        self.server_socket = None

        # Criação do socket do servidor
        self.create_socket()
        self.listen_for_messages()

    def create_socket(self):
        try:
            # Inicializa o socket do servidor como UDP
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind((self.SERVER_HOST, self.SERVER_PORT))
            print(f"Servidor iniciado e escutando na porta {self.SERVER_PORT}")
        except Exception as e:
            print(f"Erro ao configurar o socket do servidor: {e}")
            sys.exit(1)

    def listen_for_messages(self):
        print("Aguardando mensagens de clientes...")
        while True:
            try:
                # Recebe dados de qualquer cliente
                data, client_address = self.server_socket.recvfrom(1024)
                data = data.decode('utf-8')
                print(f"Dados recebidos de {client_address}: {data}")

                # Manipulação dos dados recebidos
                if data == 'pop':
                    self.send_pops(client_address)
                elif data == 'pop_received':
                    print("Confirmação recebida: Cliente recebeu os POPs com sucesso.")

            except Exception as e:
                print(f"Erro ao receber dados do cliente: {e}")

    def send_pops(self, client_address):
        try:
            # Envia a lista de POPs para o cliente
            pops_message = "Lista de POP IPs: " + ", ".join(pops)
            self.server_socket.sendto(pops_message.encode('utf-8'), client_address)
            print(f"POPs enviados para {client_address}. Aguardando confirmação...")
        except Exception as e:
            print(f"Erro ao enviar POPs: {e}")

if __name__ == "__main__":
    servidor = Servidor()





















import socket
import os

# Configurações do servidor central
SERVER_IP = '127.0.0.1'  # IP do PoP
SERVER_PORT = 10000      # Porta para o PoP
BUFFER_SIZE = 4096       # Tamanho do buffer para cada pacote UDP
VIDEO_PATH = "videos/meuvideo.mp4"

def stream_video():
    # Cria o socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Envia o vídeo em pacotes para o PoP
    with open(VIDEO_PATH, 'rb') as f:
        while True:
            # Lê um pedaço do vídeo
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            # Envia o pacote UDP para o PoP
            sock.sendto(data, (SERVER_IP, SERVER_PORT))
    
    # Fecha o socket
    sock.close()
    print("Transmissão concluída")

if __name__ == "__main__":
    stream_video()