import time
import socket

msgFromClient = "alsdna jdnasdnla sndkans nfan fanslkdjn asndjiasnd anssjd nasjbd hjasbd jasbdj absjdasb fjasj fbajsb"
msgFromClient = msgFromClient.split(" ")
serverAddressPort = ("127.0.0.1", 20001)
bufferSize = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.settimeout(1)

seq_num = 0
for msg in msgFromClient:
    msg = str(seq_num) + ":" + msg
    print("sending: " + msg)
    bytesToSend = str.encode(msg)
    # Send to server using created UDP socket}
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    while(1):
        try:
            bytesAddressPair = UDPClientSocket.recvfrom(bufferSize)
            if bytesAddressPair[0][0] == seq_num: #If the response received is the current seq_num we can continue sending the next packet
                print("Received Ack for " + str(seq_num))
                seq_num += 1
                break
            else:
                #If we received a delayed ack from a previous package
                print("Wrong ack:" + str(bytesAddressPair[0][0]))
                continue
        except socket.timeout:
            print("Timeout")
            print("resending: " + msg)
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            continue

UDPClientSocket.close()