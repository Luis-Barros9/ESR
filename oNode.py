import socket
import pickle
import sys
import threading
import time

class Node:
    def __init__(self, name):
        self.timeout = 1

        # Node name
        self.name = name

        # List of neighbours
        self.neighbours = {}

        # Distribution Tree Information
        self.flow_latency = 999
        self.flow_jump = 999
        self.flow_parent = ''

        # List of streams
        # Key:stream & Value:list of clients (neighbours)
        self.streams = {}
        self.streams_list = []

        # Create server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(('0.0.0.0', 6000))

        # RUN!!!
        self.get_neighbours_from_bootstrapper()
        threading.Thread(target=self.passthrough_streams).start()

        print('[INFO] Node running.')
        try:
            while True:
                data, addr = self.server.recvfrom(1024)
                threading.Thread(target=self.handler, args=(data, addr)).start()
        finally:
            self.server.close()

    # Handler for clients
    def handler(self, data, address):
        msg = data.decode('utf-8')
        if msg.startswith('BUILDTREE'):

            # Save better flow and send to neighbours
            ip = address[0]
            _, t, latency, jump = msg.split(':')
            total_latency = float(latency) + time.time() - float(t)
            if total_latency < self.flow_latency or (total_latency == self.flow_latency and int(jump) + 1 <= self.jump):
                self.flow_jump = int(jump) + 1
                self.flow_parent = ip
                self.flow_latency = round(total_latency, 5)
                self.build_distribution_tree(ip)
                print(f'Arvore de distribuição construída: {self.flow_parent} - {self.flow_latency} - {self.flow_jump}')

        elif msg.startswith('STREAM'):

            # Adiciona o cliente à lista de clientes de uma stream requisitada
            client = str(address[0])
            _, stream_id = msg.split()

            # Se não tem fluxo da stream, pede a stream ao nodo pai
            if stream_id not in self.streams:
                self.streams[stream_id] = []
                self.server.sendto(msg.encode('utf-8'), (self.flow_parent, 6000))

            self.streams[stream_id].append(client)

        elif msg.startswith('LISTSTREAMS'):

            # Devolve a lista de streams disponiveis
            response = self.streams_list
            self.server.sendto(response.encode(), address)

    # Build distribution tree - UDP
    def build_distribution_tree(self, address):
        for neighbour in self.neighbours:
            # Check if neighbour is NOT his parent
            if not neighbour == address:
                message = str.encode(f'BUILDTREE:{time.time()}:{self.flow_latency}:{self.flow_jump}')
                self.server.sendto(message, (neighbour, 6000))

    # Retransmit received streams packets
    def passthrough_streams(self):
        streams = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        streams.bind(('0.0.0.0', 7000))
        try:
            while True:
                data, addr = streams.recvfrom(2128)
                self.send_packet(streams, data)
        finally:
            self.server.close()

    # Send packet to clients
    def send_packet(self, socket, data):
        packet = pickle.loads(data)
        stream_id = packet['id']
        for client in self.streams[stream_id]:
            socket.sendto(data, (client, 7000))

    # Send ping to neighbours to verify if they are alive or not
    # every 60 seconds
    def keep_alive(self):
        pass

    # Get list of streams available to play from flow parent - UDP
    def get_list_of_streams(self):
        pop_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pop_conn.settimeout(self.timeout)
        while True:
            try:
                # Envia mensagem
                message = str.encode('LISTSTREAMS')
                pop_conn.sendto(message, (self.flow_parent, 6000))

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

    # Get neighbours from bootstrapper - TCP
    def get_neighbours_from_bootstrapper(self):
        bs_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Conexão com boostrapper
            bs_conn.connect(('10.0.34.2', 5000))

            # Envia mensagem
            message = str.encode(f'NEIGHBOURS {self.name}')
            bs_conn.send(message)

            # Recebe lista de vizinhos
            neighbours = pickle.loads(bs_conn.recv(2048))
            for neighbour in neighbours:
                self.neighbours[neighbour] = True # Guarda como offline
            print('Vizinhos obtidos com sucesso.')
        except:
            print('Bootstrapper offline.')
            sys.exit(1)
        finally:
            bs_conn.close()

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: oNode.py <node_name>")
        sys.exit(1)

    node = Node(sys.argv[1])
