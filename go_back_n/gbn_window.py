from _typeshed import Self
import random

CONST_MAX_SEQ_NUM = 2**16 - 1

class GbnWindow:
    def __init__(self, window_size: int):
        self.window_size = window_size
        self.base = random.randrange(0, CONST_MAX_SEQ_NUM)
        self.next_seq_num = self.window_base
        self.packet_buffer = []

    def is_full(self) -> bool:
        return (self.next_seq_num - self.base == self.window_size)

    def add_packet(self, packet: bytes):
        #TODO: PROCESAR EL PAQUETE PARA QUE TENGA TODA LA METADATA
        self.packet_buffer.append(packet)
        self.next_seq_num += 1
        #TODO: RETORNAR EL PAQUETE PROCESADO

    def acknowledge(self):
        self.base += 1
        self.packet_buffer.pop(0)

    def get_size(self):
        return self.window_size

    def get_base(self):
        return self.window_size

    def get_next_seq_num(self):
        return self.next_seq_num
    
