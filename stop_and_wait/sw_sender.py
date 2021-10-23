import sys
sys.path.insert(1, '../') #TODO wtf is this?
import general.shared_constants as shared_constants
import general.ack_constants as ack_constants
import general.atomic_udp_socket as AtomicUDPSocket
import time
import socket

class InvalidDestinationError(Exception):
    pass

class InvalidMessageSize(Exception):
    pass

class CloseSenderError(Exception):
    pass

class StopAndWaitSender:
    def __init__(self, socket: AtomicUDPSocket, base_seq_num: int):
        self.sckt = socket
        self.should_keep_running = True
        self.seq_num = base_seq_num

    def send(self, message: bytes):
        if (self.should_keep_running):
            if (len(message) + ack_constants.SEQ_NUM_SIZE <= shared_constants.CONST_MAX_BUFFER_SIZE): #-2 por los 2 bytes del seq num
                self._try_send(message)
            else:
                raise InvalidMessageSize()
        else:
            raise CloseSenderError()

    def close(self):
        self.should_keep_running = False

    #PRIVATE

    def _try_send(self, message: bytes):
        message = self.seq_num.to_bytes(ack_constants.SEQ_NUM_SIZE,"big") + message #Build message with sequence number
        self.sckt.send(message) #Send message

        #Setup timeout
        sent_time = time.time() 
        waited_time = 0
        curr_timeout = ack_constants.BASE_TIMEOUT / 1000
        self.sckt.settimeout(curr_timeout)
        
        while(1): 
            try:
                response = self.sckt.recv(ack_constants.ACK_PACKET_SIZE)#3 bytes = byte de ack + 2 bytes de seq num
                waited_time = time.time() - sent_time
                #Check if response is an ACK
                if response[0] == ack_constants.ACK_TYPE_NUM:
                    if int.from_bytes(response[1:],byteorder='big', signed=False) == self.seq_num: #If the response received is the current seq_num we can continue sending the next packet
                        self.seq_num += 1
                        break
                    else:
                        self.sckt.settimeout(curr_timeout - waited_time)
                        curr_timeout -= waited_time
                        #If we received a delayed ack from a previous package we ignore it

            except socket.timeout:
                self.sckt.send(message) #Resend message if timeout occurred
                
                #Reset timeout
                sent_time = time.time() 
                waited_time = 0
                curr_timeout = ack_constants.BASE_TIMEOUT / 1000
                self.sckt.settimeout(curr_timeout) 