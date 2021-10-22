from go_back_n.gbn_sender import GbnSender
from stop_and_wait.sw_sender import StopAndWaitSender
from general.receiver import Receiver
from general.atomic_udp_socket import AtomicUDPSocket

class ReliableUDPSocket:
    def __init__(self, use_goback_n: bool = False, port: int = None):
        self.sckt = AtomicUDPSocket(port)
        self.receiver = Receiver(self.sckt, 0) #TODO esto en realidad recibe el expected seq num primero, yo le hardcodee por ahora un 0
        if use_goback_n:
            self.sender = GbnSender(self.sckt)
        else:
            self.sender = StopAndWaitSender(self.sckt)
        