import threading
import time
from queue import Queue
import queue

from lib.go_back_n.gbn_window import GbnWindow

from lib.general.constants import *
from lib.general.atomic_udp_socket import AtomicUDPSocket
from lib.general.connection_status import ConnectionStatus


class InvalidDestinationError(Exception):
    pass


class InvalidMessageSize(Exception):
    pass


class CloseSenderError(Exception):
    pass


class GbnSender:
    def __init__(
            self,
            sender: AtomicUDPSocket,
            receiver: Queue,
            window_size: int,
            base_seq_num: int,
            connection_status: ConnectionStatus):
        self.window = GbnWindow(window_size, base_seq_num, connection_status)
        self.sender = sender
        self.receiver = receiver
        self.keep_running = True
        self.connection_status = connection_status
        self.ack_thread = threading.Thread(
            target=self._confirm_packets, daemon=True)
        self.ack_thread.start()

    def send(self, message: bytes, add_metadata: bool = True):
        if self.keep_running:
            if (len(message) <= MAX_BUFFER_SIZE):
                packet = self.window.add_packet(message, add_metadata)
                self.sender.send(packet)
            else:
                raise InvalidMessageSize()
        else:
            raise CloseSenderError()

    def close(self):
        self.keep_running = False
        self.window.close()
        self.ack_thread.join()

    # PRIVATE
    def _resend_all_packets(self):
        for packet in self.window.get_unacknowledged_packets():
            self.sender.send(packet)

    def _confirm_packets(self):
        base_timeout = PACKET_TIMEOUT / 1000
        checked_all_messages = False
        waited_time = 0
        time_until_timeout = base_timeout

        while (
                self.keep_running or not checked_all_messages) and self.connection_status.connected:
            before_recv_time = time.time()
            try:
                if self.window.wait_for_sent_packet():
                    ping_packet = self.window.add_packet(b'', add_metadata=True)
                    self.sender.send(
                        ping_packet)  # This empty message is used as a PING message, to check for connection status
                if time_until_timeout <= 0:
                    self._resend_all_packets()
                    waited_time = 0
                    time_until_timeout = base_timeout
                packet = self.receiver.get(timeout=time_until_timeout)
                waited_time += time.time() - before_recv_time
                time_until_timeout = base_timeout - waited_time
                received_seq_num = int.from_bytes(
                    packet, byteorder='big', signed=False)
                checked_all_messages = self.window.update_base(
                    received_seq_num)
                waited_time = 0
            except queue.Empty:
                time_until_timeout = 0
            except ConnectionRefusedError:  # There was a Connection Error detected by the OS (or some other kind of unknown error)
                self.connection_status.connected = False
