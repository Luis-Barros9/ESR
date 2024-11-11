import os
import socket
import threading
import pickle
from oPacket import oPacket
import time

class Server:
    def __init__(self):
        # List of videos available
        self.videos = []

        # List of streams
        self.streams = {}

        # Create server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(('0.0.0.0', 6000))

        # RUN!!!
        self.make_list_of_videos()
        self.stream_videos()

        print('[INFO] Server listening for requests.')
        try:
            while True:
                data, addr = self.server.recvfrom(1024)
                threading.Thread(target= self.handler, args=(data, addr)).start()
        finally:
            self.server.close()

    # Handler for clients
    def handler(self, data, address):
        msg = data.decode('utf-8')
        if msg.startswith('LISTSTREAMS'):

            # Devolve a lista de streams disponiveis
            response = '\n'.join(self.streams.keys())
            self.server.sendto(response, address)

        elif msg.startswith('STREAM'):

            # Adiciona o cliente à lista de clientes de uma stream requisitada
            _, stream_id = msg.split()
            self.streams[stream_id].append(str(address[0]))

    # Make list of videos available to stream
    def make_list_of_videos(self):
        folder_path = './videos'
        try:
            self.videos = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file)) and file != '.gitkeep']
        except Exception as e:
            print(f"An error occurred: {e}")
            self.videos = []

    # Stream available videos
    def stream_videos(self):
        for video in self.videos:
            self.streams[video] = []
            threading.Thread(target=self.stream_video, args=(video,)).start()
        print('[INFO] Streaming videos.')

    # Stream video - UDP
    def stream_video(self, video):
        BUFFERSIZE = 2048
        BITRATE = 2_000_000
        interval = BUFFERSIZE * 8 / BITRATE # CBR
        video_file = open('./videos/' + video, 'rb')
        while True:
            data = video_file.read(BUFFERSIZE)

            if not data:
                video_file.seek(0)
                continue

            for client in self.streams[video]:
                self.server.sendto(data, (client, 6000))
                
            time.sleep(interval)

if __name__ == "__main__":
    server = Server()