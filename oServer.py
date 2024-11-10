import os
import socket
import threading
import pickle
from oPacket import oPacket

class Server:
    def __init__(self):
        # List of videos available
        self.videos = []

        # List of clients
        self.clients = ['10.0.32.20']

        # Create server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(('0.0.0.0', 6000))

        # RUN!!!
        self.make_list_of_videos()
        self.stream_videos()

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
            threading.Thread(target=self.stream_video, args=(video,)).start()

    # Stream video - UDP
    def stream_video(self, video):
        BUFFERSIZE = 2048
        video_file = open('./videos/' + video, 'rb')
        while True:
            data = video_file.read(BUFFERSIZE)

            if not data:
                video_file.seek(0)
                continue

            for client in self.clients:
                self.server.sendto(data, (client, 6000))

if __name__ == "__main__":
    server = Server()