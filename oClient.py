import socket
import pickle
import threading
import time

class oClient:
    def __init__(self):
        self.pops = [] # Lista pontos de presença
        self.pop = '' # Ponto de presença a ser usado
        self.timeout = 3 # Tempo para timeout em segundos

        # RUN!!!
        self.get_points_of_presence()
        self.get_list_of_streams()
        self.receive_video()

    # Get points of presence from bootstrapper
    def get_points_of_presence(self):

        # Socket comunicação servidor
        bootstrapper_conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        bootstrapper_conn.settimeout(self.timeout)
        bootstrapper_conn.connect(('10.0.0.10', 6000))

        while True:
            try:
                message = str.encode('pop')
                bootstrapper_conn.send(message)
                pop_list = bootstrapper_conn.recv(1024)
                self.pops = pop_list
                print('POPs obtidos com sucesso.')
                message = str.encode('pop_received')
                bootstrapper_conn.send(message)
                break
            except socket.timeout:
                print('Timeout - Reenvio de pedido POPs.')
            except:
                print('Servidor não está a atender pedidos. Tente novamente mais tarde. :D')
                break

    # Get list of streams available to play (from POP)
    def get_list_of_streams(self):
        pass

    # Receive video from server (POP)
    def receive_video(self):
        pass

if __name__ == "__main__":
    client = oClient()