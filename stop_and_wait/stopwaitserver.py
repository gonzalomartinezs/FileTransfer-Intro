import time
import socket
import random

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

# Listen for incoming datagrams

lost_ack = True #To simulate los acknowledgements

while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize) #Receive packet
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    clientMsg = "Message Received:{}".format(message)
    #clientIP  = "Client IP Address:{}".format(address)
    print(clientMsg)
    #print(clientIP)

    # Sending a reply to client
    seq_num = int(message.decode().split(":")[0]) #The message format is: (seq_num:msg) so this line is to get the seq_num
    #Simulate lost ack
    if seq_num % 4 == 0 and lost_ack:
        lost_ack = False
        continue

    bytesToSend = seq_num.to_bytes(1,"little") #The response to the client is the seq_num we read before
    UDPServerSocket.sendto(bytesToSend, address)
    time.sleep(random.uniform(0.3, 1.2)) #To simulate network congestion
    lost_ack = True
