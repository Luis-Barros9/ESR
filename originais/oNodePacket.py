def class Packet:
    FLOOD='f'
    EXIT ='e' # abandono???
    STREAM = 's' # Stream de dados
    GET = 'g' #pedido de stream

    def __init__(self,type,timestamp=None,path=None,data=None):
        self.type = type
        self.timestamp = timestamp
        self.path = path #este será usado para o flood, como so é preciso neste caso  não sei se devia ter um campo especial so para este assim
        self.data = data # pode ser a classe do pacote de streaming
        # acrescentar partes para controlo de falhas em udp


    ## não sei se é preciso fazer decode e encodes ou basta usar apenas o FLOOD
