import os
import sys
import socket
import threading

class Server:
    def __init__(self):

        # List of videos available
        self.videos = []

        # Criação do socket do servidor
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('0.0.0.0', 6000))
        print(f"Servidor iniciado e escutando na porta 6000")

        # RUN!!!
        self.make_list_of_videos()
        threading.Thread(target=self.build_tree()).start()
        threading.Thread(target=self.stream_video()).start()

    # Make list of videos available to stream
    def make_list_of_videos(self):
        folder_path = './videos'
        try:
            self.videos = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
        except Exception as e:
            print(f"An error occurred: {e}")
            self.videos = []

    # Stream video
    def stream_video(self):
        while True:
            pass

    # Build tree of distribution
    def build_tree(self):
        pass

if __name__ == "__main__":
    servidor = Servidor()