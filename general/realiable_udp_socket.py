from general import ack_constants, shared_constants
from go_back_n.gbn_sender import GbnSender
from stop_and_wait.sw_sender import StopAndWaitSender
from general.receiver import Receiver
from general.atomic_udp_socket import AtomicUDPSocket
from queue import Queue
import threading

class ReliableUDPSocket:
    def __init__(self, use_goback_n: bool = False, port: int = None):
        self.sckt = AtomicUDPSocket(port)
        self.ack_queue = Queue()
        self.msg_queue = Queue()#TODO: TIENE QUE GUARDAR TUPLA DE ADDRESS Y MENSAJE
        self.should_keep_going = True
        self.thread = threading.Thread(target = self._receive_messages, daemon=True)
        self.thread.start()

        #TODO: VAMOS A TENER QUE PUSHEAR UN MENSAJE DE QUE SE CERRO LA COLA PARA QUE DEJE DE INTENTAR LEER Y SE BLOQUEE

        self.receiver = Receiver(self.sckt, self.msg_queue, 0) #TODO esto en realidad recibe el expected seq num primero, yo le hardcodee por ahora un 0
        if (use_goback_n):
            self.sender = GbnSender(self.sckt, self.ack_queue, 10) #TODO volar el 10 hardcodeado del window_size
        else:
            self.sender = StopAndWaitSender(self.sckt, self.ack_queue)

    def connect(self, destination_ip: str, destination_port: int):
        self.sender.set_destination(destination_ip, destination_port)
        self.receiver.set_source(destination_ip, destination_port)
        self.sender.send(shared_constants.SYN_TYPE_NUM.to_bytes(1, byteorder='big', signed=False))
        self.receiver.receive()

    def send(self, msg: bytes):
        self.sender.send(msg)

    def receive(self) -> bytes:
        return self.receiver.receive()

    def close(self):
        self.sender.close()

    #PRIVATE
    #TODO hay que chequear que los mensajes nos vengan del tipo con el que entablamos la conexion
    def _receive_messages(self): #TODO tenemos que chequear que los mensajes esten bien armados en cada caso, por ej que el mensaje de tipo ACK no tenga mas de 2 bytes despues del byte del ACK (que son los 2 bytes del seq_num)
        while (self.should_keep_going):
            packet, addr = self.sckt.recvfrom(shared_constants.CONST_MAX_BUFFER_SIZE)
            packet_type = packet[shared_constants.MSG_TYPE_INDEX]
            packet = packet[shared_constants.MSG_TYPE_INDEX+1:]
            if packet_type == ack_constants.ACK_TYPE_NUM:
                self.ack_queue.put((packet, addr))
            elif packet_type == shared_constants.MSG_TYPE_NUM:
                self.msg_queue.put((packet, addr))
