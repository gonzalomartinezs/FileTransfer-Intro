import socket
import general.shared_constants as shared_constants
from general.atomic_wrapper import AtomicWrapper
from go_back_n.gbn_window import GbnWindow
import random
import threading
import general.ack_constants as ack_constants
import time

class InvalidDestinationError(Exception):
    pass

class InvalidMessageSize(Exception):
    pass

class CloseSenderError(Exception):
    pass

class GbnSender:
    def __init__(self, window_size):
        self.destination_ip = None
        self.destination_port = None
        self.window = GbnWindow(window_size)
        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.should_keep_running = True
        self.ack_thread = threading.Thread(target=self._confirm_packets)
        self.ack_thread.start()
        
    def set_destination(self, destination_ip: str, destination_port: int):
        self.destination_ip = destination_ip
        self.destination_port = destination_port

    def send(self, message: bytes):
        if (self.should_keep_running):
            if (self.destination_ip == None) or (self.destination_port == None):
                raise InvalidDestinationError()

            if (len(bytes) <= shared_constants.CONST_MAX_BUFFER_SIZE):
                packet = self.window.add_packet(message)
                self.sckt.sendto(packet, (self.destination_ip, self.destination_port))
            else:
                raise InvalidMessageSize()
        else:
            raise CloseSenderError()

    def close(self):
        self.should_keep_running = False
        self.ack_thread.join()

    #PRIVATE

    def _resend_all_packets(self):
        for packet in self.window.get_unacknowledged_packets():
            self.sckt.sendto(packet, (self.destination_ip, self.destination_port))

    def _confirm_packets(self):
        base_timeout = ack_constants.BASE_TIMEOUT / 1000
        checked_all_messages = False
        waited_time = 0
        while (self.should_keep_running or not checked_all_messages):
            self.sckt.settimeout(base_timeout - waited_time)
            before_recv_time = time.time()
            packet, sender = self.sckt.recvfrom(ack_constants.CONST_ACK_PACKET_SIZE)
            waited_time += time.time() - before_recv_time
            if (waited_time >= base_timeout):
                waited_time = 0
                self._resend_all_packets()
            else:
                if ((sender == (self.destination_ip, self.destination_port)) and (packet[ack_constants.MESSAGE_TYPE_INDEX] == ack_constants.CONST_ACK_NUM)):
                    received_seq_num = packet[ack_constants.MESSAGE_TYPE_INDEX + 1:ack_constants.CONST_ACK_PACKET_SIZE]
                    checked_all_messages = self.window.update_base(received_seq_num)
                    #TODO: RESETEAR WAIT TIME PARA EL PROXIMO PAQUETE
                    