import socket
import pickle
import subprocess

class oClient:
    def __init__(self):
        self.pops = [] # Lista pontos de presença
        self.pop = '10.0.27.1' # Ponto de presença a ser usado
        self.timeout = 3 # Tempo para timeout em segundos

        self.streams_list = []

        # RUN!!!
        self.get_points_of_presence()
        self.get_list_of_streams()
        self.display_stream('movie.Mjpeg') # TODO Fazer menu para escolher a stream

    # Get points of presence from server - UDP
    def get_points_of_presence(self):
        server_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_conn.settimeout(self.timeout)
        while True:
            try:
                # Envia mensagem
                message = str.encode('POPS')
                server_conn.sendto(message,  ('10.0.0.10', 6000))

                # Recebe lista de POPs
                self.pops = pickle.dumps(server_conn.recv(2048))
                print('POPs obtidos com sucesso.')
            except socket.timeout:
                print('Timeout - Reenvio de pedido de lista de pops.')
                continue
            except:
                print('Servidor não está a atender pedidos.')
            finally:
                server_conn.close()
                break

    # Get list of streams available to play (from POP) - UDP
    def get_list_of_streams(self):
        pop_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pop_conn.settimeout(self.timeout)
        while True:
            try:
                # Envia mensagem
                message = str.encode('LISTSTREAMS')
                pop_conn.sendto(message, (self.pop, 6000))

                # Recebe lista de streams
                self.streams_list = pop_conn.recv(1024).decode()
                print(f'[INFO] Lista de streams obtida com sucesso. STREAMS: {self.streams_list}')
            except socket.timeout:
                print('Timeout - Reenvio de pedido de lista de streams.')
                continue
            except:
                print('Servidor não está a atender pedidos.')
            finally:
                pop_conn.close()
                break

    # Display video from server (POP) - UDP
    def display_stream(self, stream):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', 7000))

        message = str.encode(f'STREAM {stream}')
        sock.sendto(message, (self.pop, 6000))

        ffplay = subprocess.Popen(
            ['ffplay', '-i', 'pipe:0', '-f', 'mjpeg', '-hide_banner'],
            stdin=subprocess.PIPE,
            stderr=subprocess.DEVNULL)

        try:
            while True:
                data, _ = sock.recvfrom(2128)

                packet = pickle.loads(data)
                video = packet['data']

                ffplay.stdin.write(video)
                ffplay.stdin.flush()
        finally:
            sock.close()
            ffplay.stdin.close()
            ffplay.wait()

if __name__ == "__main__":
    client = oClient()
