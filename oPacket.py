class oPacket:
    def __init__(self, stream_id, type, data):
        self.stream_id = stream_id
        self.type = type
        self.data = data
        pass

    def encode(self):
        pass
    
    def decode(self):
        pass