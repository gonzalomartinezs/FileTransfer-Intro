from lib.general import ack_constants, shared_constants
from lib.general.accepted_connections import AcceptedConnections
from lib.go_back_n.gbn_sender import GbnSender
from lib.stop_and_wait.sw_sender import StopAndWaitSender
from lib.general.receiver import ClosedReceiverError, Receiver
from lib.general.atomic_udp_socket import AtomicUDPSocket
from queue import Queue
from enum import Enum
import threading
import random
import time
import socket
from lib.general.connection_status import ConnectionStatus

WINDOW_SIZE = 10


class SocketAlreadySetupError(Exception):
    pass

class ClosedSocketError(Exception):
    pass

class ReliableUDPSocketType(Enum):
    CLIENT = 1
    SERVER_LISTENER = 2
    SERVER_HANDLER = 3

class ReliableUDPSocket:
    accepted_connections = AcceptedConnections() # Used by the listeners and handlers

    def __init__(self, use_goback_n: bool = False):
        self.sckt = AtomicUDPSocket()
        self.type = None
        self.ack_queue = Queue()
        self.msg_queue = Queue()
        self.use_goback_n = use_goback_n
        self.sender = None
        self.receiver = None
        self.thread = None
        self.keep_running = True

    def bind(self, addr):
        self.sckt.bind(addr)

    # TODO agregar un timeout total en el que deje de intentar
    def connect(self, addr):
        if self.type is None:
            self.type = ReliableUDPSocketType.CLIENT
        else:
            raise SocketAlreadySetupError()

        connected = False
        base_seq_num = random.randrange(0, shared_constants.MAX_SEQ_NUM)
        base_timeout = ack_constants.BASE_TIMEOUT / 1000
        waited_time = 0
        time_until_timeout = base_timeout
        self.sckt.sendto(
            shared_constants.SYN_TYPE_NUM.to_bytes(
                1,
                byteorder='big',
                signed=False) +
            base_seq_num.to_bytes(
                2,
                byteorder='big',
                signed=False),
            addr)

        while not connected:
            before_recv_time = time.time()
            try:
                if time_until_timeout <= 0:
                    self.sckt.sendto(
                        shared_constants.SYN_TYPE_NUM.to_bytes(
                            1,
                            byteorder='big',
                            signed=False) +
                        base_seq_num.to_bytes(
                            2,
                            byteorder='big',
                            signed=False),
                        addr)
                    waited_time = 0
                    time_until_timeout = base_timeout
                self.sckt.settimeout(time_until_timeout)
                packet, r_addr = self.sckt.recvfrom(
                    2**16-1)
                waited_time += time.time() - before_recv_time
                time_until_timeout = base_timeout - waited_time
                if (r_addr[0] == addr[0]) and (r_addr[1] != addr[1]) and (
                        packet[0] == shared_constants.OK_TYPE_NUM):
                    connected = True
                    connection_seq_num = int.from_bytes(
                        packet[1:], byteorder='big', signed=False)
            except socket.timeout:
                time_until_timeout = 0

        self.sckt.settimeout(None)  # This removes the timeout we were setting
        self._initialize_connection(r_addr, base_seq_num, connection_seq_num)

    def listen(self, max_connections: int):
        if self.type is None:
            self.type = ReliableUDPSocketType.SERVER_LISTENER
        else:
            raise SocketAlreadySetupError()

        self.new_connections_queue = Queue(max_connections)
        self.thread = threading.Thread(
            target=self._listen_for_connections, daemon=True)
        self.thread.start()

    def accept(self):  # TODO indicar que esto retorna un (ReliableUDPSocket, Addr)
        c = self.new_connections_queue.get()
        if c == None:
            raise ClosedSocketError
        return c

    # Raises ConnectionRefusedError if the connection was closed
    def send(self, msg: bytes):
        if self.connection_status.connected == False:
            raise ClosedSocketError
        self.sender.send(msg)

    def recv(self, buff_size: int) -> bytes:
        if self.connection_status.connected == False:
            return b''
        try:
            return self.receiver.receive()[:buff_size]
        except ClosedReceiverError:
            return b''

    # IMPORTANT: DO NOT attempt to reuse the socket after executing close() on
    # it! Otherwhise you will get an exception!
    def close(self):
        if self.type == ReliableUDPSocketType.CLIENT:
            self.sender.close()
            self.receiver.close()
            self.keep_running = False
            self.thread.join()
            self.sckt.close()
            self.connection_status.connected = False
        elif self.type == ReliableUDPSocketType.SERVER_HANDLER:
            self.sender.close()
            self.receiver.close()
            self.keep_running = False
            self.thread.join()
            self.sckt.close()
            ReliableUDPSocket.accepted_connections.remove_connection(self.peer_addr)
            self.connection_status.connected = False
        elif self.type == ReliableUDPSocketType.SERVER_LISTENER:
            self.keep_running = False
            self.thread.join()
            self.sckt.close()
            self.new_connections_queue.put(None) # Avoids getting locked in the accept method
        # If type == None then there is nothing to be done so no error is
        # raised




    ####################### PRIVATE ####################### 

    def _initialize_connection(self,
                               dest_addr,
                               base_seq_num: int,
                               connection_seq_num: int):
        # Now we can only send and receive packets to and from this address
        self.sckt.connect(dest_addr)
        self.connection_status = ConnectionStatus()
        self.peer_addr = dest_addr
        self.receiver = Receiver(self.sckt, self.msg_queue, connection_seq_num, self.connection_status)
        if (self.use_goback_n):
            self.sender = GbnSender(
                self.sckt,
                self.ack_queue,
                WINDOW_SIZE,
                base_seq_num,
                self.connection_status)
        else:
            self.sender = StopAndWaitSender(
                self.sckt, self.ack_queue, base_seq_num, self.connection_status)
        self.thread = threading.Thread(
            target=self._receive_messages, daemon=True)
        self.thread.start()

    def _listen_for_connections(self):
        # TODO ver si hay una alternativa a un timeout para el tema del close,
        # pero creo que no hay mucha
        self.sckt.settimeout(0.5)
        while self.keep_running:
            try:
                packet, addr = self.sckt.recvfrom(
                    2**16 - 1)
                if self.new_connections_queue.full():
                    # We ignore the connection request if the queue is full
                    continue
                if (packet[0] == shared_constants.SYN_TYPE_NUM) and (
                        addr not in ReliableUDPSocket.accepted_connections):
                    connection_seq_num = int.from_bytes(
                        packet[1:], byteorder='big', signed=False)
                    n_sckt = ReliableUDPSocket(self.use_goback_n)
                    base_seq_num = random.randrange(
                        0, shared_constants.MAX_SEQ_NUM)
                    n_sckt.type = ReliableUDPSocketType.SERVER_HANDLER
                    n_sckt._initialize_connection(
                        addr, base_seq_num, connection_seq_num)
                    n_sckt.sender.send(
                        shared_constants.OK_TYPE_NUM.to_bytes(
                            1,
                            byteorder='big',
                            signed=False) +
                        base_seq_num.to_bytes(
                            2,
                            byteorder='big',
                            signed=False),
                        add_metadata=False)
                    ReliableUDPSocket.accepted_connections.add_connection(addr)
                    self.new_connections_queue.put((n_sckt, addr))
            except socket.timeout:
                pass

    def _receive_messages(self):
        # TODO ver si hay una alternativa a un timeout para el tema del close,
        # pero creo que no hay mucha
        self.sckt.settimeout(0.5)
        while self.keep_running and self.connection_status.connected:
            try:
                packet = self.sckt.recv(2**16-1) #TODO por ahora con esto agarro el tamanio maximo
                # if 90 > random.randint(0, 100):
                #     continue
                time_since_last_msg = time.time()
                packet_type = packet[0]
                # We remove the packet type before redirecting it
                packet = packet[1:]
                if (packet_type == ack_constants.ACK_TYPE_NUM) and \
                        (len(packet) == 2):
                    self.ack_queue.put(packet)
                elif (packet_type == shared_constants.MSG_TYPE_NUM) and \
                        (len(packet) >= 2):
                    self.msg_queue.put(packet)
                elif (packet_type == shared_constants.OK_TYPE_NUM) and \
                        (len(packet) == 2):
                    self.msg_queue.put(packet)
            except socket.timeout:
                if (time.time() - time_since_last_msg) > shared_constants.TIME_UNTIL_DISCONNECTION:
                    self.connection_status.connected = False
            except ConnectionRefusedError: # There was a Connection Error detected by the OS (or some other kind of unknown error)
                    self.connection_status.connected = False
