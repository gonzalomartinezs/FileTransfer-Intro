from general import ack_constants, shared_constants
from general.accepted_connections import AcceptedConnections
from go_back_n.gbn_sender import GbnSender
from stop_and_wait.sw_sender import StopAndWaitSender
from general.receiver import Receiver
from general.atomic_udp_socket import AtomicUDPSocket
from queue import Queue
from enum import Enum
import threading
import random
import time
import socket

WINDOW_SIZE = 10


class SocketAlreadySetupError(Exception):
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
                packet, r_addr = self.sckt.recvfrom(shared_constants.MAX_BUFFER_SIZE)
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
        return self.new_connections_queue.get()

    def send(self, msg: bytes):
        self.sender.send(msg)

    def recv(self, buff_size: int) -> bytes:
        return self.receiver.receive()[:buff_size]

    # IMPORTANT: DO NOT attempt to reuse the socket after executing close() on
    # it! Otherwhise you will get an exception!
    def close(self):
        if self.type == ReliableUDPSocketType.CLIENT:
            self.sender.close()
            self.receiver.close()
            self.keep_running = False
            self.thread.join()
            self.sckt.close()
        elif self.type == ReliableUDPSocketType.SERVER_HANDLER:
            self.sender.close()
            self.receiver.close()
            self.keep_running = False
            self.thread.join()
            self.sckt.close()
            ReliableUDPSocket.accepted_connections.remove_connection(self.peer_addr)
        elif self.type == ReliableUDPSocketType.SERVER_LISTENER:
            self.keep_running = False
            self.thread.join()
            self.sckt.close()
        # If type == None then there is nothing to be done so no error is
        # raised




    ####################### PRIVATE ####################### 

    def _initialize_connection(self,
                               dest_addr,
                               base_seq_num: int,
                               connection_seq_num: int):
        # Now we can only send and receive packets to and from this address
        self.sckt.connect(dest_addr)
        self.peer_addr = dest_addr
        self.receiver = Receiver(self.sckt, self.msg_queue, connection_seq_num)
        if (self.use_goback_n):
            self.sender = GbnSender(
                self.sckt,
                self.ack_queue,
                WINDOW_SIZE,
                base_seq_num)
        else:
            self.sender = StopAndWaitSender(
                self.sckt, self.ack_queue, base_seq_num)
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
                    shared_constants.MAX_BUFFER_SIZE)
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
        while self.keep_running:
            try:
                packet = self.sckt.recv(shared_constants.MAX_BUFFER_SIZE)
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
                pass
