import time
import threading
import sys
sys.path.insert(1, '../../../')  # To fix library includes

from lib.general.atomic_udp_socket import AtomicUDPSocket
from lib.general import ack_constants
from lib.general import shared_constants
from lib.general.connection_status import ConnectionStatus
from queue import Queue
import queue

MAX_PACKET_BUFF_SIZE = 10

class InvalidDestinationError(Exception):
    pass


class InvalidMessageSize(Exception):
    pass


class CloseSenderError(Exception):
    pass


class StopAndWaitSender:
    def __init__(self, sender: AtomicUDPSocket, receiver: Queue, base_seq_num: int,
                        connection_status: ConnectionStatus):
        self.sender = sender
        self.receiver = receiver
        self.should_keep_running = True
        self.seq_num = base_seq_num
        self.connection_status = connection_status
        self.keep_running = True
        self.packet_buff = queue.Queue(maxsize=MAX_PACKET_BUFF_SIZE)
        self.mutex = threading.Lock()
        self.ack_thread = threading.Thread(
            target=self._try_send, daemon=True)
        self.ack_thread.start()

    def send(self, message: bytes, add_metadata: bool = True):
        if (self.should_keep_running):
            if len(message) <= shared_constants.MAX_BUFFER_SIZE:
                packet = self._generate_packet(message, add_metadata)
                while self.connection_status.connected:
                    try:
                        self.packet_buff.put(packet, timeout=shared_constants.PING_TIMEOUT) #No se si aca tengo q hacer send o si tengo que encolar el mensaje en packetBuff
                        break
                    except queue.Full:
                        pass
            else:
                raise InvalidMessageSize()
        else:
            raise CloseSenderError()

    def close(self):
        self.keep_running = False
        self.ack_thread.join()

    # PRIVATE

    def _generate_packet(self, msg: bytes, add_metadata: bool = True) -> bytes:
        self.mutex.acquire()
        packet = msg
        if add_metadata:
            packet = (shared_constants.MSG_TYPE_NUM).to_bytes(1, byteorder='big') + self.seq_num.to_bytes(2, "big") + msg
        self.seq_num += 1
        self.mutex.release()
        return packet
    
    def _try_send(self):
        base_timeout = ack_constants.BASE_TIMEOUT / 1000
        waited_time = 0
        time_until_timeout = base_timeout
        send_next_package = True

        while (self.keep_running or not self.packet_buff.empty()) and self.connection_status.connected:
            try:
                if send_next_package:
                    try:
                        packet_to_send = self.packet_buff.get(timeout=shared_constants.PING_TIMEOUT)
                    except queue.Empty:
                        packet_to_send = self._generate_packet(b'', add_metadata=True)
                    expected_seq_num = int.from_bytes(packet_to_send[1:3], byteorder='big', signed=False)
                    self.sender.send(packet_to_send)
                    send_next_package = False
                before_recv_time = time.time()
                if time_until_timeout <= 0:
                    self.sender.send(packet_to_send)
                    waited_time = 0
                    time_until_timeout = base_timeout
                packet = self.receiver.get(timeout=time_until_timeout)
                waited_time += time.time() - before_recv_time
                time_until_timeout = base_timeout - waited_time
                received_seq_num = int.from_bytes(
                    packet, byteorder='big', signed=False)
                if received_seq_num == expected_seq_num:
                    send_next_package = True
                    time_until_timeout = base_timeout
                waited_time = 0
            except queue.Empty:
                time_until_timeout = 0
            except ConnectionRefusedError:  # There was a Connection Error detected by the OS (or some other kind of unknown error)
                self.connection_status.connected = False













        
        # # Add type byte and sequence number to the message
        # """ if add_metadata:
        #     message = (shared_constants.MSG_TYPE_NUM).to_bytes(1, byteorder='big') + self.seq_num.to_bytes(2, "big") + message """

        # self.sckt.send(message)

        # # Setup timeout
        # sent_time = time.time()
        # waited_time = 0
        # curr_timeout = ack_constants.BASE_TIMEOUT / 1000

        # while self.should_keep_running and self.connection_status.connected:
        #     try:
        #         if curr_timeout <= 0:
        #             self.sckt.send(message)  # Resend message if timeout occurred

        #             # Reset timeout
        #             sent_time = time.time()
        #             waited_time = 0
        #             curr_timeout = ack_constants.BASE_TIMEOUT / 1000

        #         # 3 bytes = byte de ack + 2 bytes de seq num
        #         #response = self.sckt.recv(ack_constants.ACK_PACKET_SIZE)
        #         response = self.receiver.get(timeout=curr_timeout)
        #         waited_time = time.time() - sent_time
        #         # Check if response is an ACK
        #         # If the response received is the current seq_num we can
        #         # continue sending the next packet
        #         if response != b'':
        #             if int.from_bytes(response, byteorder='big', signed=False) == self.seq_num:
        #                 self.seq_num += 1
        #                 break
        #             else:
        #                 curr_timeout -= waited_time
        #                 # If we received a delayed ack from a previous package
        #                 # we ignore it



        #     except queue.Empty:
        #         """ self.sckt.send(message)  # Resend message if timeout occurred

        #         # Reset timeout
        #         sent_time = time.time()
        #         waited_time = 0
        #         curr_timeout = ack_constants.BASE_TIMEOUT / 1000 """
        #         curr_timeout = 0
