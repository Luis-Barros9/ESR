import socket
import pickle
import threading
import time

class oClient:
    def __init__(self):
        self.pointsofpresence = [] # Lista pontos de presença
        self.pop = '' # Ponto de presença a ser usado
        self.timeout = 3 # Tempo para timeout em segundos

        # Socket comunicação servidor
        self.server_conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.server_conn.settimeout(self.timeout)
        self.server_conn.connect(('10.0.0.10', 6000))

        # RUN!!!
        self.get_points_of_presence()
        threading.Thread(target=self.evaluate_points_of_presence, args=(self, )).start() # Thread para monitorização de POPs

    # Get points of presence from server
    def get_points_of_presence(self):
        while True:
            try:
                message = str.encode('pop')
                self.server_conn.send(message)
                pop_list = self.server_conn.recv(1024)
                self.pointsofpresence = pop_list
                print('POPs obtidos com sucesso.')
                message = str.encode('pop_received')
                self.server_conn.send(message)
                break
            except socket.timeout:
                print('Timeout - Reenvio de pedido POPs.')
            except:
                print('Servidor não está a atender pedidos. Tente novamente mais tarde. :D')
                break

if __name__ == "__main__":
    client = oClient()

























import socket

# Configurações do cliente
CLIENT_IP = '127.0.0.1'
CLIENT_PORT = 12000
BUFFER_SIZE = 4096
OUTPUT_FILE = "meuvideo_received.mp4"

def receive_video():
    # Cria o socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((CLIENT_IP, CLIENT_PORT))
    
    # Abre o arquivo para salvar o vídeo
    with open(OUTPUT_FILE, 'wb') as f:
        print("Aguardando pacotes de vídeo do PoP...")
        
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            if not data:
                break
            f.write(data)
    
    sock.close()
    print("Vídeo recebido com sucesso")

if __name__ == "__main__":
    receive_video()