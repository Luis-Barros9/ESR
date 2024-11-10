import socket
import pickle
import threading
import subprocess

class oClient:
    def __init__(self):
        self.pops = [] # Lista pontos de presença
        self.pop = '' # Ponto de presença a ser usado
        self.timeout = 3 # Tempo para timeout em segundos

        self.streams_list = []

        # RUN!!!
        self.get_points_of_presence()
        self.get_list_of_streams()
        self.display_stream()

    # Get points of presence from bootstrapper - UDP
    def get_points_of_presence(self):
        bs_conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        bs_conn.settimeout(self.timeout)
        while True:
            try:
                message = str.encode('POPS')
                bs_conn.sendto(message, ('10.0.0.10', 6000))
                self.pops = bs_conn.recv(1024)
                print('POPs obtidos com sucesso.')
                break
            except socket.timeout:
                print('Timeout - Reenvio de pedido POPs.')
            except:
                print('Servidor não está a atender pedidos. Tente novamente mais tarde. :D')
                break

    # Get list of streams available to play (from POP) - UDP
    def get_list_of_streams(self):
        pop_conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        pop_conn.settimeout(self.timeout)
        while True:
            try:
                message = str.encode('STREAMS')
                pop_conn.sendto(message, (self.pop, 6000))
                self.streams_list = pop_conn.recv(1024)
                print('Lista de streams obtida com sucesso.')
                break
            except socket.timeout:
                print('Timeout - Reenvio de pedido de lista de streams.')
                continue
            except:
                print('Servidor não está a atender pedidos. Tente novamente mais tarde. :D')
                break

    # Display video from server (POP) - UDP
    def display_stream(self):
        BUFFERSIZE = 2048

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', 6000))

        ffplay = subprocess.Popen(['ffplay', '-i', 'pipe:0', '-f', 'mjpeg'], stdin=subprocess.PIPE)

        try:
            while True:
                data, _ = sock.recvfrom(BUFFERSIZE)

                if not data:
                    print(f"[INFO] Transmissão concluída.")
                    break

                ffplay.stdin.write(data)
                ffplay.stdin.flush()
        finally:
            sock.close()
            ffplay.stdin.close()
            ffplay.wait()

if __name__ == "__main__":
    client = oClient()