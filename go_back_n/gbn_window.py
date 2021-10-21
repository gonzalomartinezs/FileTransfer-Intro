import random
import threading
import socket

CONST_MAX_SEQ_NUM = 2**16 - 1

class GbnWindow:
    def __init__(self, window_size: int):
        self.mutex = threading.Lock()
        self.window_size = window_size
        self.base = random.randrange(0, CONST_MAX_SEQ_NUM)
        self.next_seq_num = self.base
        self.packet_buffer = []
        self.closed = False
        self.cv = threading.Condition(self.mutex)

    def add_packet(self, packet: bytes):
        self.mutex.acquire()
        while self._is_full():
            self.cv.wait()
        packet = (self.next_seq_number).to_bytes(2, byteorder='big') + packet
        self.packet_buffer.append(packet)
        self._add_to_seq_num()
        #TODO: VER SI AGREGAMOS CHEQUEO DE SI HAY QUE HACER EL NOTIFY
        self.cv.notify_all()
        self.mutex.release()
        return packet

    def acknowledge(self):
        self.mutex.acquire()
        self.base += 1
        self.packet_buffer.pop(0)
        self.mutex.release()

    def get_size(self) -> int:
        self.mutex.acquire()
        r = self.window_size
        self.mutex.release()
        return r

    def get_base(self) -> int:
        self.mutex.acquire()
        r = self.base
        self.mutex.release()
        return r

    def get_next_seq_num(self) -> int:
        self.mutex.acquire()
        r = self.next_seq_num
        self.mutex.release()
        return r


    #Function description
    #Returns True if there are not any messages whose acknowledge was not received, otherwise returns False
    def update_base(self, received_seq_number: int):
        self.mutex.acquire()

        is_sequential_case = self.base <= received_seq_number < self.next_seq_num
        is_looping_case = (self.next_seq_num < self.base) and ((self.base <= received_seq_number) or (received_seq_number < self.next_seq_num))
        if (is_sequential_case or is_looping_case):
            del self.packet_buffer[:self._get_packets_between(received_seq_number)]
            self.base = received_seq_number + 1
            if (self.base > CONST_MAX_SEQ_NUM): #This is only for the edge case where received_seq_number == CONST_MAX_SEQ_NUM
                self.base = 0
            self.cv.notify_all()
        is_buffer_empty = len(self.packet_buffer) == 0
        self.mutex.release()

        return is_buffer_empty
    
    def get_unacknowledged_packets(self):
        self.mutex.acquire()
        ret_val = self.packet_buffer
        self.mutex.release()
        return ret_val
        
    def wait_for_sent_packet(self):
        self.mutex.acquire()
        while ((len(self.packet_buffer) == 0) and not self.closed):
            self.cv.wait()
        self.mutex.release()

    def close(self):
        self.mutex.acquire()
        self.closed = True
        self.cv.notify_all()
        self.mutex.release()

    #PRIVATE
    def _is_full(self) -> bool:
        return (self.next_seq_num - self.base) == self.window_size

    def _get_packets_between(self, num):
        acknowledged_packets = 0
        aux = num - self.base
        if (aux < 0):
            acknowledged_packets = ((CONST_MAX_SEQ_NUM + 1) - self.base) + (num + 1)
        else:
            acknowledged_packets = aux + 1

        return acknowledged_packets

    def _add_to_seq_num(self):
        self.next_seq_num += 1
        if (self.next_seq_num > CONST_MAX_SEQ_NUM):
            self.next_seq_num = 0
