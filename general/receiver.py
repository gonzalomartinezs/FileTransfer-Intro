import threading
import socket
import ack_constants

PACKET_QUEUE_SIZE = 5

class ClosedSocketError(Exception):
    pass

class Receiver:
    def __init__(self, expected_seq_num):
        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = None
        self.expected_seq_num = expected_seq_num
        self.received_packets_queue = []
        self.ack_thread = threading.Thread(target=self._receive_packets)
        self.ack_thread.start()
        self.mutex = threading.Lock()
        self.cv = threading.Condition(self.mutex)
        self.should_keep_running = True
        #TODO agregar IP y port

    def set_reading_port(self, port: int):
        self.port = port

    def receive(self):
        packet = None

        if not self.should_keep_running:
            raise ClosedSocketError()

        self.mutex.acquire()
        while (len(self.received_packets_buffer) == 0):
            self.cv.wait()
        packet = self.received_packets_queue.pop(0)
        self.mutex.release()

        return packet

    def close(self):
        self.mutex.acquire()
        self.should_keep_running = False
        self.mutex.release()

    # PRIVATE
    def _receive_packets(self):
        while (self.should_keep_running):
            packet, sender_addr = self.sckt.recvfrom(ack_constants.ACK_PACKET_SIZE) #TODO hay que chequear que los mensajes nos vengan del tipo con el que entablamos la conexion
            packet_seq_number = int.from_bytes(packet[:ack_constants.SEQ_NUM_SIZE], byteorder='big', signed=False)
            self.mutex.acquire()
            if (packet_seq_number == self.expected_seq_num):
                if (len(self.received_packets_queue) < PACKET_QUEUE_SIZE):
                    self.received_packets_queue.append(packet[ack_constants.SEQ_NUM_SIZE:])
                    self.cv.notify_all() #TODO: VER SI CHEQUEAMOS QUE ANTES HUBIERA 0 PAQUETES PARA HACER EL NOTIFY
                    ack_message = (ack_constants.ACK_NUM).to_bytes(1, byteorder='big') + (self.expected_seq_num).to_bytes(2, byteorder='big')
                    self.sckt.sendto(sender_addr, ack_message)
                    self.expected_seq_num += 1
            else:
                ack_message = (ack_constants.ACK_NUM).to_bytes(1, byteorder='big') + (self.expected_seq_num-1).to_bytes(2, byteorder='big')
                self.sckt.sendto(sender_addr, ack_message)
            self.mutex.release()
