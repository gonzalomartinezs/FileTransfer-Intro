import socket
import general.shared_constants as shared_constants

class InvalidDestinationError(Exception):
    pass

class ClientSocket:
    def __init__(self):
        self.destination_ip = None
        self.destination_port = None
        #self.sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Ip y puerto al que conectar
    def connect_to(self, ip: str, port: int):

        #Aca hace el protocolo de conexion

        #Si falla la conexion hay que tirar una exception


        self.destination_ip = ip
        self.destination_port = port


    def send(self, message: bytes):
        if (self.destination_ip == None or self.destination_port == None):
            raise InvalidDestinationError()

        if (len(bytes) > shared_constants.CONST_MAX_BUFFER_SIZE):
            self.sckt.sendto(message, (self.destination_ip, self.destination_port))
    