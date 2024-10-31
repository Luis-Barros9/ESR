import socket
import pickle
import threading
import time

# 60 segundos 
MONITOR_INTERVAL = 60

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

    def evaluate_point(self,ponto):
        # TODO avaliar métricas como largura de banda, perda, números de saltos...
        return 1

    def evaluate_points_of_presence(self):
        # avaliar pontos de presenca
        if len(self.pointsofpresence):
            best = self.pointsofpresence[0]
            max = self.evaluate_point(best)

            # escolher o melhor ponto de presença no momento
            for p in self.pointsofpresence[1:]:
                rate = self.evaluate_point(p)
                if rate > max:
                    max = rate
                    best = p
            self.pop = best
    
    def monitor_points_of_presence(self):
        while True:
            self.evaluate_points_of_presence()
            time.sleep(MONITOR_INTERVAL)

    def start(self):
        self.get_points_of_presence()
        #threading.Thread(target=self.evaluate_points_of_presence, args=(self)).start()

if __name__ == "__main__":
    

    client = oClient()
    client.start()