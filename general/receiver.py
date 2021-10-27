import threading
import general.ack_constants as ack_constants
from general.atomic_udp_socket import AtomicUDPSocket
import general.shared_constants as shared_constants
from queue import Queue

PACKET_QUEUE_SIZE = 5


class ClosedSocketError(Exception):
    pass

class Receiver:
    def __init__(
            self,
            sender: AtomicUDPSocket,
            receiver: Queue,
            expected_seq_num: int):
        self.sender = sender
        self.receiver = receiver
        self.expected_seq_num = expected_seq_num
        self.received_packets_queue = Queue(PACKET_QUEUE_SIZE)
        self.keep_running = True
        self.ack_thread = threading.Thread(
            target=self._receive_packets, daemon=True)
        self.ack_thread.start()

    def receive(self) -> bytes:
        if not self.keep_running:
            raise ClosedSocketError()
        return self.received_packets_queue.get()

    def close(self):
        self.keep_running = False
        # This avoids getting blocked in the receiver.get() method call
        self.receiver.put(None)
        self.ack_thread.join()

    # PRIVATE
    def _receive_packets(self):
        packet = self.receiver.get()
        while (self.keep_running):
            packet_seq_number = int.from_bytes(
                packet[:2], byteorder='big', signed=False)
            if (packet_seq_number == self.expected_seq_num):
                if not self.received_packets_queue.full():
                    if packet[2:] != b'': # This avoids pushing the OK null body as an actual message
                        self.received_packets_queue.put(packet[2:])
                    ack_message = (
                        ack_constants.ACK_TYPE_NUM).to_bytes(
                        1, byteorder='big', signed=False) + (
                        self.expected_seq_num).to_bytes(
                        2, byteorder='big', signed=False)
                    self.sender.send(ack_message)
                    self.expected_seq_num += 1
            else:
                last_ack_seq_num = (self.expected_seq_num - 1) if self.expected_seq_num != 0 else shared_constants.MAX_SEQ_NUM
                ack_message = (ack_constants.ACK_TYPE_NUM).to_bytes(1, byteorder='big', signed=False) + (last_ack_seq_num - 1).to_bytes(2, byteorder='big', signed=False)
                self.sender.send(ack_message)
            packet = self.receiver.get()
