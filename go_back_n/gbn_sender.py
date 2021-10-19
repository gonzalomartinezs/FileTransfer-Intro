import socket
import general.shared_constants as shared_constants
from general.atomic_wrapper import AtomicWrapper
from gbn_window import GbnWindow
import random
import threading
import general.ack_constants as ack_constants
import time

class InvalidDestinationError(Exception):
    pass

class InvalidMessageSize(Exception):
    pass

class GbnSender:
    def __init__(self, window_size):
        self.destination_ip = None
        self.destination_port = None
        self.window = GbnWindow(window_size)
        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ack_thread = threading.Thread(self._confirm_packets)
        self.should_keep_running = True
        
    def set_destination(self, destination_ip: str, destination_port: int):
        self.destination_ip = destination_ip
        self.destination_port = destination_port

    def send(self, message: bytes):
        if (self.destination_ip == None) or (self.destination_port == None):
            raise InvalidDestinationError()

        if self.window.is_full():
            pass
            # TODO aca nos iriamos a dormir hasta que la CV del que recibe los ACK nos despierte al confirmarse el ACK del packet base
     
        if (len(bytes) <= shared_constants.CONST_MAX_BUFFER_SIZE):
            packet = self.window.add_packet(message)
            self.sckt.sendto(packet, (self.destination_ip, self.destination_port))
        else:
            raise InvalidMessageSize()

    def close(self):
        self.should_keep_running = False

    #PRIVATE
    def _confirm_packets(self):
        base_timeout = ack_constants.BASE_TIMEOUT / 1000
        checked_all_messages = False
        while (self.should_keep_running or not checked_all_messages):
            waited_time = 0
            self.sckt.settimeout(base_timeout - waited_time)
            before_recv_time = time.time()
            packet, sender = self.sckt.recvfrom(ack_constants.CONST_ACK_PACKET_SIZE)
            waited_time += time.time() - before_recv_time
            if (waited_time >= base_timeout):
                pass
                #TODO se trigereo un timeout, tenemos que reenviar los packets desde base hasta next_seq_number - 1
            else:
                if ((sender == (self.destination_ip, self.destination_port)) and (packet[ack_constants.MESSAGE_TYPE_INDEX] == ack_constants.CONST_ACK_NUM)):
                    received_seq_num = packet[ack_constants.MESSAGE_TYPE_INDEX + 1:ack_constants.CONST_ACK_PACKET_SIZE]
                    self.window.update_base(received_seq_num)
                    #TODO: SACAR DEL CACHE DE PAQUETES TODOS LOS PAQUETES HASTA EL QUE SE ACKNOWLEDGEO

            #TODO: UPDATEAR checked_all_messages PARA QUE SE VAYA DEL LOOP CUANDO TERMINEN DE MANDARSE TODOS LOS MENSAJES
            #      TAMBIEN VAMOS A TENER QUE UPDATEARLA CUANDO SE RECIBAN MENSAJES NUEVOS, AUNQUE PUEDE CHEQUEARSE MIRANDO SI HAY DATOS EN
            #      EL CACHE DE MENSAJES DE LOS CUALES HAY QUE CONFIRMAR SU ACK