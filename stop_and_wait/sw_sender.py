import sys
sys.path.insert(1, '../')
import general.shared_constants as shared_constants
import general.ack_constants as ack_constants
import general.atomic_udp_socket as AtomicUDPSocket
import time
import random
import socket

class InvalidDestinationError(Exception):
    pass

class InvalidMessageSize(Exception):
    pass

class CloseSenderError(Exception):
    pass

class StopAndWaitSender:
    def __init__(self, socket: AtomicUDPSocket):
        self.destination_ip = None
        self.destination_port = None
        #self.sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sckt = socket
        self.should_keep_running = True
        self.seq_num = 0 #Should be random
        
    def set_destination(self, destination_ip: str, destination_port: int):
        self.destination_ip = destination_ip
        self.destination_port = destination_port

    def send(self, message: bytes):
        if (self.should_keep_running):
            if (self.destination_ip == None) or (self.destination_port == None):
                raise InvalidDestinationError()

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
        self.sckt.sendto(message, (self.destination_ip, self.destination_port)) #Send message

        #Setup timeout
        sent_time = time.time() 
        waited_time = 0
        curr_timeout = ack_constants.BASE_TIMEOUT / 1000
        self.sckt.settimeout(curr_timeout)
        
        while(1): 
            try:
                response, sender = self.sckt.recvfrom(ack_constants.ACK_PACKET_SIZE)#3 bytes = byte de ack + 2 bytes de seq num
                waited_time = time.time() - sent_time
                #Check if response is an ACK and if it is from the address we are sending to
                if (response[0] == ack_constants.ACK_TYPE_NUM) and (sender == (self.destination_ip, self.destination_port)):
                    if int.from_bytes(response[1:],byteorder='big', signed=False) == self.seq_num: #If the response received is the current seq_num we can continue sending the next packet
                        self.seq_num += 1
                        break
                    else:
                        self.sckt.settimeout(curr_timeout - waited_time)
                        curr_timeout -= waited_time
                        #If we received a delayed ack from a previous package we ignore it

            except socket.timeout:
                self.sckt.sendto(message, (self.destination_ip, self.destination_port)) #Resend message if timeout occurred
                
                #Reset timeout
                sent_time = time.time() 
                waited_time = 0
                curr_timeout = ack_constants.BASE_TIMEOUT / 1000
                self.sckt.settimeout(curr_timeout) 
                continue