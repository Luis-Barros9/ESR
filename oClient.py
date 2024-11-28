import socket
import pickle
import threading
import subprocess
import time
from colorama import Back, Style

class oClient:
    def __init__(self):
        self.pops = [] # Lista pontos de presença
        self.pop = '' # Ponto de presença a ser usado
        self.timeout = 1 # Tempo para timeout em segundos

        self.stream_choosen = ''
        self.streams_list = []

        # Client socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', 6000))
        self.socket.settimeout(self.timeout)

        # RUN!!!
        self.get_points_of_presence()
        threading.Thread(target=self.monitor_points_of_presence).start()        
        self.get_list_of_streams()

        # Escolhe uma stream da lista de streams disponiveis
        print('Escolha a stream:')
        for stream in self.streams_list:
            print(stream)
        self.stream_choosen = input()

        # Display stream
        self.request_stream()
        self.display_stream()

    # Get points of presence from server - UDP
    def get_points_of_presence(self):
        while True:
            try:
                # Envia mensagem
                message = str.encode('POPS')
                self.socket.sendto(message,  ('10.0.0.10', 6000))

                # Recebe lista de POPs
                self.pops = pickle.loads(self.socket.recv(2048))
                print(Back.GREEN + '[SUCCESS] Pontos de presença obtidos com sucesso.' + Style.RESET_ALL)
                break
            except socket.timeout:
                print(Back.YELLOW + '[WARNING] Timeout - Reenvio de pedido de lista de pontos de presença.' + Style.RESET_ALL)
            except:
                print(Back.RED + '[FAIL] Servidor não está a atender pedidos.' + Style.RESET_ALL)
                self.socket.close()
                break

    # Get list of streams available to play (from POP) - UDP
    def get_list_of_streams(self):
        while self.pop == '':
            time.sleep(1)

        while True:
            try:
                # Envia mensagem
                message = str.encode('LISTSTREAMS')
                self.socket.sendto(message, (self.pop, 6000))

                # Recebe lista de streams
                self.streams_list = pickle.loads(self.socket.recv(1024))
                print(Back.GREEN + f'[SUCCESS] Lista de streams obtida com sucesso. STREAMS: {self.streams_list}' + Style.RESET_ALL)
                break
            except socket.timeout:
                print(Back.YELLOW + '[WARNING] Timeout - Reenvio de pedido de lista de streams.' + Style.RESET_ALL)
                continue
            except:
                print(Back.RED + '[FAIL] Servidor não está a atender pedidos.' + Style.RESET_ALL)
                self.socket.close()
                break

    # Request stream - UDP
    def request_stream(self):
        tries = 0
        while True:
            if tries > 3:
                break
            try:
                # Envia mensagem
                message = str.encode(f'STREAM {self.stream_choosen}')
                self.socket.sendto(message, (self.pop, 6000))

                # Recebe confirmação
                response = self.socket.recv(1024)
                if response.decode() == 'OKAY':
                    break
            except socket.timeout:
                print(Back.YELLOW + '[WARNING] Timeout - Reenvio de pedido de stream.' + Style.RESET_ALL)
                tries += 1
                continue
            except:
                print(Back.RED + '[FAIL] Servidor não está a atender pedidos.' + Style.RESET_ALL)
                self.socket.close()
                break

    # Cancel stream - UDP
    def cancel_stream(self):
        tries = 0
        while True:
            if tries > 3:
                break;
            try:
                # Envia mensagem
                message = str.encode(f'NOSTREAM {self.stream_choosen}')
                self.socket.sendto(message, (self.pop, 6000))

                # Recebe confirmação
                response = self.socket.recv(1024)
                if response.decode() == 'OKAY':
                    break
            except socket.timeout:
                print(Back.YELLOW + '[WARNING] Timeout - Reenvio de pedido para cancelar stream.' + Style.RESET_ALL)
                tries += 1
                continue
            except:
                print(Back.RED + '[FAIL] Servidor não está a atender pedidos.' + Style.RESET_ALL)
                self.socket.close()
                break

    # Display video from server (POP) - UDP
    def display_stream(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', 7000))

        ffplay = subprocess.Popen(
            ['ffplay', '-i', 'pipe:0', '-hide_banner', '-infbuf'],
            stdin=subprocess.PIPE,
            stderr=subprocess.DEVNULL)

        try:
            while True:
                data, _ = sock.recvfrom(2200)

                packet = pickle.loads(data)
                video = packet['data']

                ffplay.stdin.write(video)
                ffplay.stdin.flush()
        except:
            print(Back.RED + f'[FAIL] Erro a mostrar stream' + Style.RESET_ALL)
        finally:
            self.cancel_stream()
            sock.close()
            ffplay.stdin.close()
            ffplay.wait()

######## MONITORIZAÇÃO DE POPS POR PARTE DO CLIENTE ########
    def monitor_points_of_presence(self):
        while True:
            valores = {}
            for pop in self.pops:
                try:
                    msg = str.encode('PING')
                    start = time.time()
                    self.socket.sendto(msg, (pop, 6000))
                    response = self.socket.recv(1024)
                    response = response.decode()
                    if response:
                        _, latency = response.split(':')
                        end = time.time()
                        volta = start - end
                        valores[pop] = (round(volta + float(latency), 5))
                except socket.timeout:
                    print(Back.YELLOW + '[WARNING] Timeout - Reenvio de pedido PING.' + Style.RESET_ALL)
                    continue

            menor = 999
            current_pop = self.pop
            for pop in valores:
                if valores[pop] < menor:
                    self.pop = pop
                    menor = valores[pop]
                    print(f'O ponto de presença foi alterado para {self.pop}')

            if current_pop != self.pop and self.stream_choosen != '':
                self.cancel_stream() # Cancela stream vinda do pop atual
                self.request_stream() # Pede a stream ao novo pop

            time.sleep(60)

if __name__ == "__main__":
    client = oClient()