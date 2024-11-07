import socket
import threading
import time
import subprocess
import multiprocessing
import re
import pickle

# 60 segundos 
MONITOR_INTERVAL = 60
NUMBER_PINGS = 10
PING_SIZE = 128
BOOTSTRAPPER_IP = '10.0.34.2'  # IP of the bootstrapper
POP_PORT = 5000

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
                for n in neighbors_for_ip:
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
    # ter em conta que podemos comunicar com vários pops ao mesmo tempo, ou seja usar portas diferentes para avaliação, mas ter cuidado
    def evaluate_point(self, ponto, porta):
        try:
            # Cria um socket UDP

            # Fazer um for para obter uma avaliação mais precisa do ponto específico
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Associa o socket à porta local
            udp_socket.bind(('', porta))
            
            # Define o endereço do ponto (IP e porta)
            ponto_address = (ponto, POP_PORT)
            
            # Envia uma mensagem de teste para o ponto
            udp_socket.sendto("Evaluate ".encode('utf-8'), ponto_address)
            
            # Recebe a resposta do ponto
            response, addr = udp_socket.recvfrom(4096)
            #o nodo deve responder com métricas de avaliação do ponto e um timestamp de envio de mensagem
            #Provavelmente acrescentar 'lixo' para simular o tamanho da mensagem ser igual ao tamanho de um pacote de streaming

            # Fecha o socket
            udp_socket.close()
            
            return 1
        except Exception as e:
            print(f'Erro ao estabelecer conexão UDP com o ponto: {e}')
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
            #self.evaluate_points_of_presence()
            self.evaluate_points_of_presence_parallel()
            time.sleep(MONITOR_INTERVAL)

    def start(self):
        self.get_points_of_presence()
        threading.Thread(target=self.monitor_points_of_presence, args=()).start()

if __name__ == "__main__":

    

    client = oClient()
    client.start()