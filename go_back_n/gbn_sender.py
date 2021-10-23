from general.atomic_udp_socket import AtomicUDPSocket
import general.shared_constants as shared_constants
from go_back_n.gbn_window import GbnWindow
import threading
import general.ack_constants as ack_constants
import general.shared_constants as shared_constants
import time
from queue import Queue
import queue


class InvalidDestinationError(Exception):
    pass

class InvalidMessageSize(Exception):
    pass

class CloseSenderError(Exception):
    pass

class GbnSender:
    def __init__(self, sender: AtomicUDPSocket, receiver: Queue, window_size: int, base_seq_num: int):
        self.destination_ip = None
        self.destination_port = None
        self.window = GbnWindow(window_size, base_seq_num)
        self.sender = sender
        self.receiver = receiver
        self.should_keep_running = True
        self.ack_thread = threading.Thread(target=self._confirm_packets, daemon=True)
        self.ack_thread.start()

    def set_destination(self, addr: tuple[str, int]):
        self.destination_ip = addr[0]
        self.destination_port = addr[1]

    def send(self, message: bytes, add_metadata: bool = True):
        if (self.should_keep_running):
            if (self.destination_ip == None) or (self.destination_port == None):
                raise InvalidDestinationError()

            if ((len(message) + shared_constants.METADATA_SIZE) <= shared_constants.CONST_MAX_BUFFER_SIZE):
                packet = self.window.add_packet(message, add_metadata)
                self.sender.sendto(packet, (self.destination_ip, self.destination_port))
            else:
                raise InvalidMessageSize()
        else:
            raise CloseSenderError()

    def close(self):
        self.should_keep_running = False
        self.receiver.put((None, None)) # This avoids possibly wainting forever in the receiver.get() call
        self.window.close()
        self.ack_thread.join()

    #PRIVATE
    def _resend_all_packets(self):
        for packet in self.window.get_unacknowledged_packets():
            self.sender.sendto(packet, (self.destination_ip, self.destination_port))

    def _confirm_packets(self):
        base_timeout = ack_constants.BASE_TIMEOUT / 1000
        checked_all_messages = False
        waited_time = 0
        time_until_timeout = base_timeout

        while (self.should_keep_running or not checked_all_messages):
            before_recv_time = time.time()
            self.window.wait_for_sent_packet()
            try:
                if time_until_timeout <= 0:
                    self._resend_all_packets()
                    waited_time = 0
                    time_until_timeout = base_timeout
                packet, sender = self.receiver.get(timeout=time_until_timeout)
                if packet == None: # If we received None because of an error, ignore it, otherwise it was because we need to close
                    continue
                waited_time += time.time() - before_recv_time
                time_until_timeout = base_timeout - waited_time
                if (sender == (self.destination_ip, self.destination_port)):
                    received_seq_num = int.from_bytes(packet, byteorder='big', signed=False)
                    checked_all_messages = self.window.update_base(received_seq_num)
                    waited_time = 0
            except queue.Empty:
               time_until_timeout = 0
