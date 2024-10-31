# Class Servidor

import sys, socket

# Dict with POPs
pops = ['10.0.27.1',
        '10.0.26.1',
		'10.0.24.1',
		'10.0.14.1']

class Servidor:    

	def __init__(self):
	    # Establishes variables
	    self.SERVER_PORT = 6000
	    self.SERVER_HOST = '0.0.0.0'  # Allows connections from any IP
	    self.server_socket = None
	
	    # Creates necessary data structures
	    self.connections = []  # List to keep track of active connections	
	    # Set up the server socket
	    self.create_socket()
	    self.listen_for_connections()

	def create_socket(self):
	    try:
	        # Initialize the server socket
	        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	        self.server_socket.bind((self.SERVER_HOST, self.SERVER_PORT))
	        print(f"Server started and listening on port {self.SERVER_PORT}")
	    except Exception as e:
	        print(f"Error setting up server socket: {e}")
	        sys.exit(1)

	def listen_for_connections(self):
	    self.server_socket.listen(5)  # Allows up to 5 connections in queue
	    while True:
	        print("Waiting for a connection...")
	        client_socket, client_address = self.server_socket.accept()
	        print(f"Connection established with {client_address}")
	        self.connections.append(client_socket)
	        self.handle_client(client_socket)

	def handle_client(self, client_socket):
	    try:
	        while True:
	            try:
	                data = client_socket.recv(1024)
	                data = data.decode('utf-8')
	                print(f"Received data: {data}")
	
	                # Handling the data
	                if data == 'pop':
	                    self.send_pops(client_socket)
	                elif data == 'pop_received':
	                    print("Confirmation received: Client successfully received POPs.")
	            except socket.timeout:
	                print("Timeout - No response received. Retrying...")
	                client_socket.sendall(b"Server timeout, waiting for response...")
	    except Exception as e:
	        print(f"Error handling client: {e}")
	    finally:
	        client_socket.close()
	        print("Client disconnected.")

	def send_pops(self, client_socket):
	    try:
	        pops = "List of POP IPs"  # Replace with actual data as needed
	        client_socket.sendall(pops.encode('utf-8'))
	        print("POPs sent. Waiting for client confirmation...")
	
	        # Set a short timeout while waiting for the confirmation
	        client_socket.settimeout(5.0)
	
	        # Waiting for confirmation message 'pop_received'
	        confirmation = client_socket.recv(1024).decode('utf-8')
	        if confirmation == 'pop_received':
	            print("Client confirmed receipt of POPs.")
	        else:
	            print("Unexpected message received instead of confirmation.")
	    except socket.timeout:
	        print("Timeout - Client did not confirm receipt of POPs. Retrying...")
	        client_socket.sendall(b"Server timeout, retrying POPs data transmission.")
	    except Exception as e:
	        print(f"Error sending POPs: {e}")

if __name__ == "__main__":
    servidor = Servidor()