from os import sendfile
import time
import socket
import random

import sys
sys.path.insert(1, '../general')
import file_reader



def receive_file(skt, filename, bufferSize):
    f = open(filename, "w")

    #lost_ack = True #To simulate los acknowledgements

    recv_seq_num = 0 #This will have to be random
    while(True):
        try:
            bytesAddressPair = skt.recvfrom(4096) #Receive packet
            message = bytesAddressPair[0]
            address = bytesAddressPair[1]#Check if im receiving from the correct adress

            # Sending a reply to client
            received_seq_num = int(message.decode().split(":",1)[0]) #The message format is: (seq_num:msg) so this line is to get the seq_num
            #Search a more efficient way to do this. Perhaps received_seq_num = int(message.decode()[:index(":")]) or something like that
            print("Received seq_num: {}".format(received_seq_num))

            if (received_seq_num == recv_seq_num):
                print("Writing to file seq_num: {}".format(received_seq_num))
                f.write(message.decode().split(":", 1)[1])#So it doestn write seq_num:
                #Search a more efficient way to do this. Perhaps received_seq_num = int(message.decode()[:index(":")]) or something like that
                recv_seq_num += 1

            #The response will be something like a specific byte meaning ACK and the sequence number
            bytesToSend = received_seq_num.to_bytes(1,"big") #Dont know if it should be little or big
            print("Sending response to seq_num: {}".format(received_seq_num))
            skt.sendto(bytesToSend, address)
            time.sleep(random.uniform(0.3, 1.2)) #To simulate network congestion
            #lost_ack = True
        except socket.timeout:
                    print("Timeout")
                    break


    f.close()


def send_file(skt, filename, adress_to, bufferSize):
    reader = file_reader.FileReader(filename)

    should_continue_reading = True

    seq_num = 0
    while (should_continue_reading):
        try:
            bytes = reader.read_next_section(4094)#4094 + 2 bytes(del seq_num) = 4096bytes q es el buffer size
            msg = seq_num.to_bytes(2,"big")
            msg = msg + bytes 
            print("Sending seq_num: {}".format(seq_num))
            skt.sendto(msg, adress_to) 
            while(1): 
                try:
                    bytesAddressPair = skt.recvfrom(3)#3 bytes = byte de ack + 2 bytes de seq num
                    if int(bytesAddressPair[0][1:]) == seq_num: #If the response received is the current seq_num we can continue sending the next packet
                        print("Received Ack for " + str(seq_num))
                        seq_num += 1
                        break
                    else:
                        #If we received a delayed ack from a previous package
                        print("Wrong ack:" + str(bytesAddressPair[0][1:]))
                        continue
                except socket.timeout:
                    print("Timeout")
                    print("resending: {}".format(seq_num))
                    skt.sendto(msg, adress_to)
                    continue
        except EOFError:
            should_continue_reading = False