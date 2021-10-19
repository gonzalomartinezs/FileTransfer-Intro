import random
import threading

CONST_MAX_SEQ_NUM = 2**16 - 1

class GbnWindow:
    def __init__(self, window_size: int):
        self.mutex = threading.Lock()
        self.window_size = window_size
        self.base = random.randrange(0, CONST_MAX_SEQ_NUM)
        self.next_seq_num = self.window_base
        self.packet_buffer = []

    def is_full(self) -> bool:
        self.mutex.acquire()
        r = self.next_seq_num - self.base == self.window_size
        self.mutex.release()
        return r

    def add_packet(self, packet: bytes):
        self.mutex.acquire()
        #TODO: PROCESAR EL PAQUETE PARA QUE TENGA TODA LA METADATA
        self.packet_buffer.append(packet)
        self.next_seq_num += 1
        #TODO: RETORNAR EL PAQUETE PROCESADO
        self.mutex.release()

    def acknowledge(self):
        self.mutex.acquire()
        self.base += 1
        self.packet_buffer.pop(0)
        self.mutex.release()

    def get_size(self):
        self.mutex.acquire()
        r = self.window_size
        self.mutex.release()
        return r

    def get_base(self):
        self.mutex.acquire()
        r = self.base
        self.mutex.release()
        return r

    def get_next_seq_num(self):
        self.mutex.acquire()
        r = self.next_seq_num
        self.mutex.release()
        return r

    def update_base(self, received_seq_number: int):
        self.mutex.acquire()
        
        if self.base <= received_seq_number < self.next_seq_num:
            self.base = received_seq_number + 1
        elif self.next_seq_num < self.base:
            if (self.base <= received_seq_number) or (received_seq_number < self.next_seq_num):
                self.base = received_seq_number + 1

        self.mutex.release()
    