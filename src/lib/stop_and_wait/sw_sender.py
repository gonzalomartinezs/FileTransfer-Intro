import queue
from queue import Queue
from lib.general.connection_status import ConnectionStatus
from lib.general.constants import *
from lib.general.atomic_udp_socket import AtomicUDPSocket
import time
import threading
import sys
sys.path.insert(1, '../../../')  # To fix library includes


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
        self.packet_buff = queue.Queue(maxsize=PACKET_QUEUE_SIZE)
        self.mutex = threading.Lock()
        self.ack_thread = threading.Thread(
            target=self._try_send, daemon=True)
        self.ack_thread.start()

    def send(self, message: bytes, add_metadata: bool = True):
        if (self.should_keep_running):
            if len(message) <= MAX_BUFFER_SIZE:
                packet = self._generate_packet(message, add_metadata)
                while self.connection_status.connected:
                    try:
                        # No se si aca tengo q hacer send o si tengo que
                        # encolar el mensaje en packetBuff
                        self.packet_buff.put(packet, timeout=PING_TIMEOUT)
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
            packet = (MSG_TYPE_NUM).to_bytes(1, byteorder='big') + \
                self.seq_num.to_bytes(2, "big") + msg
        self.seq_num += 1
        if self.seq_num > MAX_SEQ_NUM:
            self.seq_num = 0
        self.mutex.release()
        return packet

    def _try_send(self):
        base_timeout = PACKET_TIMEOUT / 1000
        waited_time = 0
        time_until_timeout = base_timeout
        send_next_package = True

        while (self.keep_running or not self.packet_buff.empty()
               ) and self.connection_status.connected:
            try:
                if send_next_package:
                    try:
                        packet_to_send = self.packet_buff.get(
                            timeout=PING_TIMEOUT)
                    except queue.Empty:
                        packet_to_send = self._generate_packet(
                            b'', add_metadata=True)
                    expected_seq_num = int.from_bytes(
                        packet_to_send[1:3], byteorder='big', signed=False)
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
            # There was a Connection Error detected by the OS (or some other
            # kind of unknown error)
            except ConnectionRefusedError:
                self.connection_status.connected = False
