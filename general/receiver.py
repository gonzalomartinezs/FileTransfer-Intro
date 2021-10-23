import threading
import general.ack_constants as ack_constants
from general.atomic_udp_socket import AtomicUDPSocket
import general.shared_constants as shared_constants
from queue import Queue

PACKET_QUEUE_SIZE = 5

class ClosedSocketError(Exception):
    pass

class Receiver:
    def __init__(self, sender: AtomicUDPSocket, receiver: Queue, expected_seq_num: int):
        self.sender = sender
        self.receiver = receiver
        self.source_ip, self.source_port = None, None
        self.expected_seq_num = expected_seq_num
        self.received_packets_queue: list[bytes] = []
        self.mutex = threading.Lock()
        self.cv = threading.Condition(self.mutex)
        self.should_keep_running = True
        self.ack_thread = threading.Thread(target=self._receive_packets, daemon=True)
        self.ack_thread.start()

    def receive(self) -> bytes:
        packet = None

        if not self.should_keep_running:
            raise ClosedSocketError()

        self.mutex.acquire()
        while (len(self.received_packets_queue) == 0):
            self.cv.wait()
        packet = self.received_packets_queue.pop(0)
        self.mutex.release()

        return packet

    def set_source(self, source_ip: str, source_port: int):
        self.source_ip, self.source_port = source_ip, source_port

    def close(self):
        self.should_keep_running = False

    # PRIVATE
    def _receive_packets(self):
        while (self.should_keep_running):
            packet, sender_addr = self.receiver.get() #TODO agregar chequeo de ip y port del mensaje
            packet_seq_number = int.from_bytes(packet[:shared_constants.SEQ_NUM_SIZE], byteorder='big', signed=False)
            self.mutex.acquire()
            if (packet_seq_number == self.expected_seq_num):
                if (len(self.received_packets_queue) < PACKET_QUEUE_SIZE):
                    self.received_packets_queue.append(packet[shared_constants.SEQ_NUM_SIZE:])
                    self.cv.notify_all() #TODO: VER SI CHEQUEAMOS QUE ANTES HUBIERA 0 PAQUETES PARA HACER EL NOTIFY
                    ack_message = (ack_constants.ACK_TYPE_NUM).to_bytes(1, byteorder='big', signed=False) + (self.expected_seq_num).to_bytes(2, byteorder='big', signed=False)
                    self.sender.sendto(ack_message, sender_addr)
                    self.expected_seq_num += 1
            else:
                latest_ack_seq_num = (self.expected_seq_num - 1) if self.expected_seq_num != 0 else shared_constants.MAX_SEQ_NUM
                ack_message = (ack_constants.ACK_TYPE_NUM).to_bytes(1, byteorder='big', signed=False) + (self.expected_seq_num-1).to_bytes(2, byteorder='big', signed=False)
                self.sender.sendto(ack_message, sender_addr)
            self.mutex.release()
