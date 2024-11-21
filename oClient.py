import socket
import pickle
import threading
import subprocess
import time
import multiprocessing
from colorama import Back, Style

class oClient:
    def __init__(self):
        self.pops = [] # Lista pontos de presença
        self.pop = '' # Ponto de presença a ser usado
        self.timeout = 3 # Tempo para timeout em segundos

        self.streams_list = []

        # RUN!!!
        self.get_points_of_presence()
        threading.Thread(target=self.monitor_points_of_presence)
        self.get_list_of_streams()

        # Escolhe uma stream da lista de streams disponiveis
        print('Escolha a stream:')
        for stream in self.streams_list:
            print(stream)
        stream = input()

        # Display stream
        self.display_stream(stream)

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
                print(Back.GREEN + '[SUCCESS] Pontos de presença obtidos com sucesso.' + Style.RESET_ALL)
                server_conn.close()
                break
            except socket.timeout:
                print(Back.YELLOW + '[WARNING] Timeout - Reenvio de pedido de lista de pontos de presença.' + Style.RESET_ALL)
            except:
                print(Back.RED + '[FAIL] Servidor não está a atender pedidos.' + Style.RESET_ALL)
                server_conn.close()
                break

    # Get list of streams available to play (from POP) - UDP
    def get_list_of_streams(self):
        pop_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pop_conn.settimeout(self.timeout)
        while True:
            try:
                if self.pop == '':
                    time.sleep(1)

                # Envia mensagem
                message = str.encode('LISTSTREAMS')
                pop_conn.sendto(message, (self.pop, 6000))

                # Recebe lista de streams
                self.streams_list = pop_conn.recv(1024).decode()
                print(Back.GREEN + f'[SUCCESS] Lista de streams obtida com sucesso. STREAMS: {self.streams_list}' + Style.RESET_ALL)
                pop_conn.close()
                break
            except socket.timeout:
                print(Back.YELLOW + '[WARNING] Timeout - Reenvio de pedido de lista de streams.' + Style.RESET_ALL)
                continue
            except:
                print(Back.RED + '[FAIL] Servidor não está a atender pedidos.' + Style.RESET_ALL)
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
        except:
            print(Back.RED + '[FAIL] Erro a mostrar stream.' + Style.RESET_ALL)
        finally:
            sock.close()
            ffplay.stdin.close()
            ffplay.wait()
            message = str.encode('NOSTREAM')
            sock.sendto(message, (self.pop, 6000))

######## MONITORIZAÇÃO DE POPS POR PARTE DO CLIENTE ########
    def monitor_points_of_presence(self):
        while True:
            self.evaluate_points_of_presence_parallel()
            time.sleep(60)

    def evaluate_points_of_presence_parallel(self):
        # avaliar pontos de presenca
        if len(self.pops):
            with multiprocessing.Pool(processes=len(self.pops)) as pool:
                avaliacoes = pool.map(self.evaluate_point, self.pops)

            print(avaliacoes)
            best = self.pops[avaliacoes.index(min(avaliacoes))]
            print('O melhor ponto de presença é: %s' % best)
            if self.pop != best:
                print('O ponto de presença foi alterado de %s para %s' % (self.pop, best))
                self.pop = best
                # Executar algum tipo de alteração???

    def evaluate_point(self, ponto):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(2)
                print(f'Avaliando PoP {ponto}')
                s.connect((ponto, 6000))
                # Enviar mensagem de teste
                message = 'PING'
                falhas = 0
                valores = []
                for _ in range(10):
                    #start = time.time()
                    s.send(message.encode())
                    data = s.recv(1024)

                    if data:
                        ## falta cuidado com duplicados
                        info = pickle.loads(data)
                        latenciaPOP = info['state'] #Estado da rede CDN entre servidor->PoP
                        end = time.time()
                        volta = end-info.timestamp
                        valores.append(volta + latenciaPOP)
                    else:
                        falhas+=1
                        print("Packet loss")
                if valores:
                    media = sum(valores)/len(valores)
                    for _ in falhas:
                        valores.append(10*media) # penalizar falhas
                    media_pen = sum(valores)/(len(valores))
                    print(f'Média de RTT para {ponto}: {media_pen}')
                    return media_pen
                else:# nenhum pacote recebido
                    return 10000
        except Exception as e:
            print(Back.RED + f'[FAIL] Erro ao avaliar PoP {ponto}: {e}' + Style.RESET_ALL)
            return 10000

if __name__ == "__main__":
    client = oClient()