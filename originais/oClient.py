import socket
import threading
import time
import subprocess
import multiprocessing
import re
import json

# 60 segundos 
MONITOR_INTERVAL = 60
NUMBER_PINGS = 10
PING_SIZE = 128

class oClient:
    def __init__(self):
        self.pointsofpresence = [] # Lista pontos de presença
        self.pop = '' # Ponto de presença a ser usado
        self.timeout = 3 # Tempo para timeout em segundos

        # Socket comunicação servidor
        self.server_conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.server_conn.settimeout(self.timeout)
        self.server_conn.connect(('10.0.0.10', 6000))

    # Get points of presence from server
    def get_points_of_presence(self):
        while True:
            try:
                message = str.encode('pop')
                self.server_conn.send(message)
                pop_list = self.server_conn.recv(1024).decode('utf-8')
                self.pointsofpresence = json.loads(pop_list)
                print(self.pointsofpresence)
                print('POPs obtidos com sucesso.')
                message = str.encode('pop_received')
                self.server_conn.send(message)
                break
            except socket.timeout:
                print('Timeout - Reenvio de pedido POPs.')
            except:
                print('Servidor não está a atender pedidos. Tente novamente mais tarde. :D')
                break

    def evaluate_point(self,ponto):
        # TODO avaliar métricas como largura de banda,latência, perda, números de saltos...
        # usar pings com prai 10 vezes ou algo assim
        try:
            output = subprocess.check_output(['ping', '-c', str(NUMBER_PINGS),'-s', str(PING_SIZE), '-q',ponto]).decode('utf-8')
                    # Extrai o tempo de resposta de cada pacote recebido
            print(output)
            stats_match = re.search(r'(\d+) packets transmitted, (\d+) received,.*?(\d+)% packet loss', output)
            if stats_match:
                transmitted_packets = int(stats_match.group(1))
                received_packets = int(stats_match.group(2))
                packet_loss = int(stats_match.group(3))
            else:
                transmitted_packets = received_packets = packet_loss = None

            # Extrai valores de RTT min, avg, max, mdev
            rtt_match = re.search(r'rtt min/avg/max/mdev = (\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)', output)
            if rtt_match:
                rtt_min = float(rtt_match.group(1))
                rtt_avg = float(rtt_match.group(2))
                rtt_max = float(rtt_match.group(3))
                rtt_mdev = float(rtt_match.group(4))
            else:
                rtt_min = rtt_avg = rtt_max = rtt_mdev = None
            print('Ponto de presença: %s' % ponto)
            print('Pacotes enviados: %d' % transmitted_packets)
            print('Pacotes recebidos: %d' % received_packets)
            print('Perda de pacotes: %d%%' % packet_loss)
            print('RTT min/avg/max/mdev = %.3f/%.3f/%.3f/%.3f ms' % (rtt_min, rtt_avg, rtt_max, rtt_mdev))
            return 1

        except subprocess.CalledProcessError:
            print('Erro no subprocesso.')
            return -1

    def evaluate_points_of_presence(self):
        # avaliar pontos de presenca
        # versão sequencial provavelmente vai ser apagada
        if len(self.pointsofpresence):

            avaliacoes = []
            for p in self.pointsofpresence:
                avaliacoes.append(self.evaluate_point(p))
            best = self.pointsofpresence[avaliacoes.index(max(avaliacoes))]
            print('O melhor ponto de presença é: %s' % best)
            self.pop = best

    def evaluate_points_of_presence_parallel(self):
        # avaliar pontos de presenca
        if len(self.pointsofpresence):
            with multiprocessing.Pool(processes=len(self.pointsofpresence)) as pool:
                avaliacoes = pool.map(self.evaluate_point, self.pointsofpresence)

            print(avaliacoes)


    
    def monitor_points_of_presence(self):
        while True:
            self.evaluate_points_of_presence()
            time.sleep(MONITOR_INTERVAL)

    def start(self):
        self.get_points_of_presence()
        threading.Thread(target=self.evaluate_points_of_presence_parallel, args=()).start()

if __name__ == "__main__":
    

    client = oClient()
    client.start()