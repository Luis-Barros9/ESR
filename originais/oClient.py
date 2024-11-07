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
            best = self.pointsofpresence[avaliacoes.index(max(avaliacoes))]
            print('O melhor ponto de presença é: %s' % best)
            if self.pop != best:
                print('O ponto de presença foi alterado de %s para %s' % (self.pop, best))
                self.pop = best
                # Executar algum tipo de alteração???


    
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