from general import ack_constants, shared_constants
from go_back_n.gbn_sender import GbnSender
from stop_and_wait.sw_sender import StopAndWaitSender
from general.receiver import Receiver
from general.atomic_udp_socket import AtomicUDPSocket
from general.accepted_connections import AcceptedConnections
from queue import Queue
import threading
import random
import time
import socket

class ReliableUDPSocket:
    def __init__(self, use_goback_n: bool = False, port: int = None):
        self.sckt = AtomicUDPSocket(port)
        self.accepted_connectons = None
        self.ack_queue = Queue()
        self.msg_queue = Queue()#TODO: TIENE QUE GUARDAR TUPLA DE ADDRESS Y MENSAJE
        self.use_goback_n = use_goback_n
        self.sender = None
        self.receiver = None
        self.thread = None
        self.should_keep_going = True
        self.base_seq_num = random.randrange(0, shared_constants.MAX_SEQ_NUM)
        #TODO: VAMOS A TENER QUE PUSHEAR UN MENSAJE DE QUE SE CERRO LA COLA PARA QUE DEJE DE INTENTAR LEER Y SE BLOQUEE

        
    #TODO BUG no se por que a veces el timeout se me hace negativo, VER ESO
    def connect(self, addr: tuple[str, int]): #TODO agregar un timeout total en el que deje de intentar
        connected = False
        base_timeout = ack_constants.BASE_TIMEOUT / 1000
        waited_time = 0
        self.sckt.sendto(shared_constants.SYN_TYPE_NUM.to_bytes(1, byteorder='big', signed=False) + self.base_seq_num.to_bytes(2, byteorder='big', signed=False), addr)

        while not connected:
            time_until_timeout = base_timeout - waited_time
            before_recv_time = time.time()
            try:
                print(time_until_timeout)
                self.sckt.settimeout(time_until_timeout)
                packet, r_addr = self.sckt.recvfrom(shared_constants.CONST_MAX_BUFFER_SIZE)
                print(packet)
                waited_time += time.time() - before_recv_time
                if (r_addr[0] == addr[0]) and (r_addr[1] != addr[1]) and (packet[0] == shared_constants.OK_TYPE_NUM):
                    connected = True
                    connection_port = r_addr[1]
                    connection_seq_num = int.from_bytes(packet[1:3], byteorder='big', signed=False)
            except socket.timeout:
                self.sckt.sendto(shared_constants.SYN_TYPE_NUM.to_bytes(1, byteorder='big', signed=False) + self.base_seq_num.to_bytes(2, byteorder='big', signed=False), addr)
                waited_time = 0

        self.sckt.settimeout(None) #This removes the timeout
        self._initialize_connection(addr, connection_seq_num)


    def listen(self): #TODO, por ahora solo la uso para setear el accepted_connections
        self.accepted_connectons = AcceptedConnections()

    def accept(self): #TODO indicar que devuelve un dato de tipo ReliableUDPSocket
        connection_accepted = False

        while not connection_accepted:
            packet, addr = self.sckt.recvfrom(shared_constants.CONST_MAX_BUFFER_SIZE)
            if (packet[0] == shared_constants.SYN_TYPE_NUM) and (not addr in self.accepted_connectons):
                connection_seq_num = int.from_bytes(packet[1:3], byteorder='big', signed=False)
                n_sckt = ReliableUDPSocket(self.use_goback_n)
                n_sckt.accepted_connectons = self.accepted_connectons
                n_sckt._initialize_connection(addr, connection_seq_num)
                n_sckt.sender.send(shared_constants.OK_TYPE_NUM.to_bytes(1, byteorder='big', signed=False) + self.base_seq_num.to_bytes(2, byteorder='big', signed=False), False)
                self.accepted_connectons.add_connection(addr)
                connection_accepted = True

        return n_sckt
        

    def send(self, msg: bytes):
        self.sender.send(msg)

    def receive(self) -> bytes:
        return self.receiver.receive()

    def close(self): #TODO borrar del AcceptedConnections el addr asignado si es que el socket fue creado por un accept
        self.sender.close()



    #PRIVATE
    def _initialize_connection(self, dest_addr: tuple[str, int], connection_seq_num: int): #TODO el base_seq_num en realidad tengo que cambiarlo en el accept todo el tiempo, sino todos los sockets tienen el mismo!
        self.receiver = Receiver(self.sckt, self.msg_queue, connection_seq_num)
        if (self.use_goback_n):
            self.sender = GbnSender(self.sckt, self.ack_queue, 10, self.base_seq_num) #TODO volar el 10 hardcodeado del window_size
        else:
            self.sender = StopAndWaitSender(self.sckt, self.ack_queue, self.base_seq_num)
        self.sender.set_destination(dest_addr)
        self.thread = threading.Thread(target = self._receive_messages, daemon=True)
        self.thread.start()


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
            elif packet_type == shared_constants.OK_TYPE_NUM:
                self.msg_queue.put((packet, addr))
