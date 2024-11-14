import socket
import threading
import time
import subprocess
import multiprocessing
import re
import pickle
from oNodePacket import Packet

# 60 segundos 
MONITOR_INTERVAL = 60
NUMBER_PINGS = 10
PING_SIZE = 128
BOOTSTRAPPER_IP = '10.0.34.2'  # IP of the bootstrapper
PORT = 5000
STREAM_SIZE = 1024 #alterar dps secalhar

class oClient:
    def __init__(self):
        self.pointsofpresence = [] # Lista pontos de presença
        self.pop = '' # Ponto de presença a ser usado
        self.timeout = 3 # Tempo para timeout em segundos

        # Socket comunicação PoP escolhido ????
        self.server_conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


    # Get points of presence from server
    def get_points_of_presence(self):
        # Connect to bootstrapper to request neighbors for each IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as bootstrapper_socket:
            try:
                bootstrapper_socket.connect((BOOTSTRAPPER_IP, PORT))
                print("[INFO] Connected to bootstrapper")
                message = f"PoPs"  # Request neighbors for this node
                print("[INFO] Requesting PoPs from bootstrapper...")
                bootstrapper_socket.send(message.encode('utf-8'))
                # Receive the list of neighbors from bootstrapper
                response = bootstrapper_socket.recv(4096)
                pops = pickle.loads(response)
                for n in pops:
                    self.pointsofpresence.append(n)
                print(f"[INFO] PoPs received from bootstrapper: {pops}")
            
            except Exception as e:
                print(f"[ERROR] Failed to retrieve PoPs from bootstrapper: {e}")

    '''
    def evaluate_point(self,ponto): 
        # criar protocolo para avaliação entrre cliente-pop -> pop deve entre outros parametros enviar dados sobre a sua conexão ao servidor
        # TODO avaliar métricas como largura de banda,latência, perda, números de saltos...
        # usar pings com prai 10 vezes ou algo assim
        try:
            output = subprocess.check_output(['ping', '-c', str(NUMBER_PINGS),'-s', str(PING_SIZE), '-q',ponto]).decode('utf-8')
                    # Extrai o tempo de resposta de cada pacote recebido
            #print(output)
            stats_match = re.search(r'(\d+) packets transmitted, (\d+) received(?:, \+?(\d+) duplicates)?, (\d+)% packet loss', output)
            if stats_match:
                transmitted_packets = int(stats_match.group(1))
                received_packets = int(stats_match.group(2))
                duplicate_packets = int(stats_match.group(3)) if stats_match.group(3) else 0
                packet_loss = int(stats_match.group(4))
            else:
                transmitted_packets = duplicate_packets = received_packets = packet_loss = None
            # Extrai valores de RTT min, avg, max, mdev
            rtt_match = re.search(r'rtt min/avg/max/mdev = \d+\.\d+/(\d+\.\d+)/\d+\.\d+/(\d+\.\d+)', output)
            if rtt_match:
                rtt_avg = float(rtt_match.group(1))
                rtt_mdev = float(rtt_match.group(2))
            else:
                rtt_avg = rtt_mdev = None
            #Debug
            print('POP: %s\nPacotes enviados: %d | Pacotes recebidos: %d | Perda de pacotes: %d%% | Pacotes duplicados: %d | RTT avg/mdev: %.2f/%.2f ms' %
      (ponto, transmitted_packets, received_packets, packet_loss, duplicate_packets or 0, rtt_avg, rtt_mdev))

            # Avaliar estado de rede com os dados passados

            # TODO melhorar a avaliação, para tornar algo mais completo, englobando mais parametros como desvio e duplicados
            # e mais cuidados com o packet loss
            if packet_loss == 100:
                return -1000
                # valores negativos porque quanto menor o tempo, melhor a rede
            return -(rtt_avg * 100.0) / (100.0 - packet_loss)

        except subprocess.CalledProcessError:
            print('Erro no subprocesso.')
            return -10000
    '''

    def evaluate_point(self,ponto):
        # criar conexão UDP com o PoP
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(2)#timeout de 2 segundos
                print(f'Avaliando PoP {ponto}')
                s.connect((ponto, PORT))
                # Enviar mensagem de teste
                message = Packet(Packet.PING)
                falhas =0
                valores = []
                for _ in range(NUMBER_PINGS):
                    #start = time.time()
                    s.send(message.encode())
                    data = s.recv(STREAM_SIZE)

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
            print(f'Erro ao avaliar PoP {ponto}: {e}')
            return 10000



    def evaluate_points_of_presence(self):
        # avaliar pontos de presenca
        # versão sequencial provavelmente vai ser apagada
        if len(self.pointsofpresence):

            avaliacoes = []
            for p in self.pointsofpresence:
                avaliacoes.append(self.evaluate_point(p))
            best = self.pointsofpresence[avaliacoes.index(max(avaliacoes))]
            print('O melhor ponto de presença é: %s' % best)
            if self.pop != best:
                print('O ponto de presença foi alterado de %s para %s' % (self.pop, best))
                self.pop = best
                # Executar algum tipo de alteração???

    def evaluate_points_of_presence_parallel(self):
        # avaliar pontos de presenca
        if len(self.pointsofpresence):
            with multiprocessing.Pool(processes=len(self.pointsofpresence)) as pool:
                avaliacoes = pool.map(self.evaluate_point, self.pointsofpresence)

            print(avaliacoes)
            best = self.pointsofpresence[avaliacoes.index(min(avaliacoes))]
            print('O melhor ponto de presença é: %s' % best)
            if self.pop != best:
                print('O ponto de presença foi alterado de %s para %s' % (self.pop, best))
                self.pop = best
                # Executar algum tipo de alteração???


    
    def monitor_points_of_presence(self):
        while True:
            #self.evaluate_points_of_presence()
            self.evaluate_points_of_presence_parallel()
            time.sleep(MONITOR_INTERVAL)

    def start(self):
        self.get_points_of_presence()
        threading.Thread(target=self.monitor_points_of_presence, args=()).start()

if __name__ == "__main__":

    

    client = oClient()
    client.start()