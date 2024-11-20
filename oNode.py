import socket
import threading
import pickle
import sys
import time
from oNodePacket import Packet

PORT = 6000  # Define a single, fixed port for all oNode instances
BOOTSTRAPPER_IP = '10.0.34.2'  # IP of the bootstrapper

class ONode:
    def __init__(self, node_name):
        self.neighbours = {} # Initialize an empty neighbors list

        self.name = node_name # Node name -- Important to distinguish this node from others
        
                # Distribution Tree Information
        self.flow_latency = 999
        self.flow_jump = 999
        self.flow_parent = ''
    

        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(('0.0.0.0', 6000))
        print(f"[INFO] oNode running on port {PORT}, waiting for connections...")

        # Track active connections
        self.connections = {}  # Dictionary to store connections with each neighbor

        # Request neighbors from bootstrapper at startup
        self.get_neighbours_from_bootstrapper()
        threading.Thread(target=self.keep_alive).start()
        threading.Thread(target=self.passthrough_streams).start()

        print('[INFO] Node running.')
        try:
            while True:
                data, addr = self.server.recvfrom(1024)
                threading.Thread(target=self.handler, args=(data, addr)).start()
        finally:
            self.server.close()

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
                self.neighbours[neighbour] = False # Guarda como offline
            print('Vizinhos obtidos com sucesso.')
        except:
            print('Bootstrapper offline.')
            sys.exit(1)
        finally:
            bs_conn.close()



    def state(self):
        # TODO  alterar função para calcular estado do nó(latência até ao servidor)
        return 1
    
        # Send ping to neighbours to verify if they are alive or not
    # every 60 seconds
    def keep_alive(self):
        while True:
            for neighbour in self.neighbours.keys():
                self.server.sendto('KEEPALIVE'.encode('utf-8'), (neighbour, 6000))
            time.sleep(60)

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

    def handler(self, data, address):
        msg = Packet.decode(data)
        if not msg:
            print(f"[ERROR] Invalid packet received from {address}")
            return

        if msg.type == Packet.PING:
            print(f"[MESSAGE] Received from {address}: PING")
            data = {"timestamp": time.time(), "state": self.state()} 
            encoded_data = pickle.dumps(data)
            padding = b'\x00' * (1024 - len(encoded_data))
            self.server.sendto(encoded_data + padding, address)

        elif msg.type == Packet.BUILDTREE:

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

        elif msg.type == Packet.STREAM:

            # Adiciona o cliente à lista de clientes de uma stream requisitada
            client = str(address[0])
            _, stream_id = msg.split()

            # Se não tem fluxo da stream, pede a stream ao nodo pai
            if stream_id not in self.streams:
                self.streams[stream_id] = []
                self.server.sendto(msg.encode('utf-8'), (self.flow_parent, 6000))

            if client not in self.streams[stream_id]:
                self.streams[stream_id].append(client)

        elif msg.type == Packet.NOSTREAM:

            # Remove o cliente da lista de clientes de uma stream
            client = str(address[0])
            _, stream_id = msg.split()
            if stream_id in self.streams:
                self.streams[stream_id].remove(client)
                self.server.sendto(msg.encode('utf-8'), (self.flow_parent, 6000))

        elif msg.type == Packet.PARENT:
            # Devolve o IP do nodo pai
            response = self.flow_parent.encode()
            self.server.sendto(response, address)

    def build_distribution_tree(self, address):
        for neighbour in self.neighbours:
            # Check if neighbour is NOT his parent
            if not neighbour == address:
                message = str.encode(f'BUILDTREE:{time.time()}:{self.flow_latency}:{self.flow_jump}')
                self.server.sendto(message, (neighbour, 6000))


    def listen_for_connections(self):
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                client_handler = threading.Thread(target=self.handle_conection, args=(client_socket, addr))
                client_handler.start()
            except Exception as e:
                print(f"[ERROR] Accepting connection: {e}")


    def listen_to_neighbor(self, client_socket, neighbor):
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"[MESSAGE] Received from {neighbor}: {message}")
        except ConnectionResetError:
            print(f"[INFO] Connection reset by {neighbor}")
        finally:
            client_socket.close()
            print(f"[INFO] Connection to {neighbor} closed")
            del self.connections[neighbor]  # Remove from active connections

    def start(self):
        threading.Thread(target=self.listen_for_connections).start()


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

    
if __name__ == "__main__":
    # Checking usage
    if len(sys.argv) != 2:
        print("Usage: python3 oNode.py <node_name>")
        sys.exit(1)

    # Storing node name (first arg)
    node_name = sys.argv[1]
    node = ONode(node_name)
    # Start the oNode
    node.start()
