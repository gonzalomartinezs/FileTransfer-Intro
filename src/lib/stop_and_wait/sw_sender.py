import time
import sys
sys.path.insert(1, '../../../')  # To fix library includes

from lib.general.atomic_udp_socket import AtomicUDPSocket
from lib.general import ack_constants
from lib.general import shared_constants
from lib.general.connection_status import ConnectionStatus
from queue import Queue
import queue


class InvalidDestinationError(Exception):
    pass


class InvalidMessageSize(Exception):
    pass


class CloseSenderError(Exception):
    pass


class StopAndWaitSender:
    def __init__(self, socket: AtomicUDPSocket, receiver: Queue, base_seq_num: int,
                        connection_status: ConnectionStatus):
        self.sckt = socket
        self.receiver = receiver
        self.should_keep_running = True
        self.seq_num = base_seq_num
        self.connection_status = connection_status

    def send(self, message: bytes, add_metadata: bool = True):
        if (self.should_keep_running):
            if (len(message) + shared_constants.METADATA_SIZE <=
                    shared_constants.MAX_BUFFER_SIZE):
                self._try_send(message, add_metadata)
            else:
                raise InvalidMessageSize()
        else:
            raise CloseSenderError()

    def close(self):
        self.should_keep_running = False

    # PRIVATE

    def _try_send(self, message: bytes, add_metadata: bool):
        # Add type byte and sequence number to the message
        if add_metadata:
            message = (shared_constants.MSG_TYPE_NUM).to_bytes(1, byteorder='big') + self.seq_num.to_bytes(2, "big") + message

        self.sckt.send(message)

        # Setup timeout
        sent_time = time.time()
        waited_time = 0
        curr_timeout = ack_constants.BASE_TIMEOUT / 1000

        while self.should_keep_running and self.connection_status.connected:
            try:
                if curr_timeout <= 0:
                    self.sckt.send(message)  # Resend message if timeout occurred

                    # Reset timeout
                    sent_time = time.time()
                    waited_time = 0
                    curr_timeout = ack_constants.BASE_TIMEOUT / 1000

                # 3 bytes = byte de ack + 2 bytes de seq num
                #response = self.sckt.recv(ack_constants.ACK_PACKET_SIZE)
                response = self.receiver.get(timeout=curr_timeout)
                waited_time = time.time() - sent_time
                # Check if response is an ACK
                # If the response received is the current seq_num we can
                # continue sending the next packet
                if response != b'':
                    if int.from_bytes(response, byteorder='big', signed=False) == self.seq_num:
                        self.seq_num += 1
                        break
                    else:
                        curr_timeout -= waited_time
                        # If we received a delayed ack from a previous package
                        # we ignore it



            except queue.Empty:
                """ self.sckt.send(message)  # Resend message if timeout occurred

                # Reset timeout
                sent_time = time.time()
                waited_time = 0
                curr_timeout = ack_constants.BASE_TIMEOUT / 1000 """
                curr_timeout = 0
