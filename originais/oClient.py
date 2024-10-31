import socket
import pickle

class oClient:
    def __init__(self):
        self.pointsofpresence = []

    def get_points_of_presence(self):
        conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        server = ('', )
        message = str.encode('pop')
        conn.sendto(message, server)
        pop = conn.recvfrom(1024)
        self.pointsofpresence = pop

    def start(self):
        self.get_points_of_presence()

if __name__ == "__main__":
    client = oClient()
    client.start()