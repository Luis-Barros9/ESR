import socket
import pickle
import threading
import subprocess

class oClient:
    def __init__(self):
        self.pops = [] # Lista pontos de presença
        self.pop = '10.0.0.10' # Ponto de presença a ser usado
        self.timeout = 3 # Tempo para timeout em segundos

        self.streams_list = []

        # RUN!!!
        self.get_points_of_presence()
        self.get_list_of_streams()
        self.display_stream()

    # Get points of presence from bootstrapper - TCP
    def get_points_of_presence(self):
        bs_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Conexão com bootstrapper
            bs_conn.connect(('10.0.34.2', 5000))

            # Envia mensagem
            message = str.encode('POPS')
            bs_conn.send(message)
            
            # Recebe lista de POPs
            self.pops = bs_conn.recv(1024)
            print('POPs obtidos com sucesso.')
        except:
            print('Bootstrapper offline.')
        finally:
            bs_conn.close()

    # Get list of streams available to play (from POP) - UDP
    def get_list_of_streams(self):
        pop_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pop_conn.settimeout(self.timeout)
        while True:
            try:
                message = str.encode('LISTSTREAMS')
                pop_conn.sendto(message, (self.pop, 6000))
                self.streams_list = pop_conn.recv(1024).decode()
                print(f'[INFO] Lista de streams obtida com sucesso. STREAMS: {self.streams_list}')
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

        message = str.encode('STREAM movie.Mjpeg')
        sock.sendto(message, ('10.0.0.10', 6000))

        ffplay = subprocess.Popen(
            ['ffplay', '-i', 'pipe:0', '-f', 'mjpeg', '-hide_banner', ], #"-loglevel", "quiet"
            stdin=subprocess.PIPE)

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
