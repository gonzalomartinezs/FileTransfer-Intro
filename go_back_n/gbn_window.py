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

        is_sequential_case = self.base <= received_seq_number < self.next_seq_num
        is_looping_case = (self.next_seq_num < self.base) and ((self.base <= received_seq_number) or (received_seq_number < self.next_seq_num))
        if (is_sequential_case or is_looping_case):
            del self.packet_buffer[:self._get_packets_between(received_seq_number)]
            self.base = received_seq_number + 1
            if (self.base > CONST_MAX_SEQ_NUM): #This is only for the edge case where received_seq_number == CONST_MAX_SEQ_NUM
                self.base = 0

        self.mutex.release()
    

    #PRIVATE
    def _get_packets_between(self, num):
        acknowledged_packets = 0
        aux = num - self.base
        if (aux < 0):
            #TODO: CHEQUEAR SI ESTA CUENTA ESTA BIEN
            acknowledged_packets = ((CONST_MAX_SEQ_NUM + 1) - self.base) + (num + 1)
        else:
            #TODO: CHEQUEAR SI ESTA CUENTA ESTA BIEN
            acknowledged_packets = aux + 1

        return acknowledged_packets