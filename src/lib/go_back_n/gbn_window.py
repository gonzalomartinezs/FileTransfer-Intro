import threading
from lib.general import shared_constants
import time
from lib.general.connection_status import ConnectionStatus


class GbnWindow:
    def __init__(self, window_size: int, base_seq_num: int, connection_status: ConnectionStatus):
        self.mutex = threading.Lock()
        self.window_size = window_size
        self.base = base_seq_num
        self.next_seq_num = self.base
        self.packet_buffer = []
        self.closed = False
        self.cv = threading.Condition(self.mutex)
        self.connection_status = connection_status

    def add_packet(self, packet: bytes, add_metadata: bool):
        self.mutex.acquire()
        while self._is_full() and self.connection_status.connected:
            self.cv.wait(timeout=shared_constants.PING_TIMEOUT)
        if not self.connection_status.connected:
            self.mutex.release()
            raise ConnectionRefusedError
        if add_metadata:
            packet = (shared_constants.MSG_TYPE_NUM).to_bytes(1, byteorder='big') + (self.next_seq_num).to_bytes(2, byteorder='big') + packet
        self.packet_buffer.append(packet)
        self._add_to_seq_num()
        self.cv.notify_all()
        self.mutex.release()
        return packet


    # Returns True if there are not any messages whose acknowledge was not
    # received, otherwise returns False
    def update_base(self, received_seq_number: int) -> bool:
        self.mutex.acquire()

        is_sequential_case = self.base <= received_seq_number and \
            received_seq_number < self.next_seq_num
        is_looping_case = (
            self.next_seq_num < self.base) and (
            (self.base <= received_seq_number) or (
                received_seq_number < self.next_seq_num))
        if (is_sequential_case or is_looping_case):
            del self.packet_buffer[:self._get_packets_between(
                received_seq_number)]
            self.base = received_seq_number + 1
            # This is only for the edge case where received_seq_number ==
            # CONST_MAX_SEQ_NUM
            if (self.base > shared_constants.MAX_SEQ_NUM):
                self.base = 0
            self.cv.notify_all()
        is_buffer_empty = (len(self.packet_buffer) == 0)

        self.mutex.release()
        return is_buffer_empty

    def get_unacknowledged_packets(self):
        self.mutex.acquire()
        ret_val = self.packet_buffer
        self.mutex.release()
        return ret_val

    # Returns true if it has to send a PING message, false otherwise
    def wait_for_sent_packet(self) -> bool:
        self.mutex.acquire()
        base_time = time.time()
        time_waited = 0
        while (len(self.packet_buffer) == 0) and (time_waited < shared_constants.PING_TIMEOUT) and not self.closed:
            self.cv.wait(timeout = shared_constants.PING_TIMEOUT)
            time_waited = time.time() - base_time
        self.mutex.release()
        return time_waited > shared_constants.PING_TIMEOUT

    def close(self):
        self.mutex.acquire()
        self.closed = True
        self.cv.notify_all()
        self.mutex.release()

    # PRIVATE
    def _is_full(self) -> bool:
        #return (self.next_seq_num - self.base) == self.window_size
        return (self._get_packets_between(self.next_seq_num) == self.window_size)

    def _get_packets_between(self, num):
        acknowledged_packets = 0
        aux = num - self.base
        if (aux < 0):
            acknowledged_packets = ((shared_constants.MAX_SEQ_NUM + 1) - self.base) + (num + 1)
        else:
            acknowledged_packets = aux + 1

        return acknowledged_packets

    def _add_to_seq_num(self):
        self.next_seq_num += 1
        if (self.next_seq_num > shared_constants.MAX_SEQ_NUM):
            self.next_seq_num = 0
