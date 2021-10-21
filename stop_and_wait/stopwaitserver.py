import protocol
import socket

""" def receive_file(skt, filename, bufferSize):
    f = open(filename, "w")

    #lost_ack = True #To simulate los acknowledgements

    server_seq_num = 0 #This will have to be random
    while(True):
        try:
            bytesAddressPair = skt.recvfrom(bufferSize) #Receive packet
            message = bytesAddressPair[0]
            address = bytesAddressPair[1]#Check if im receiving from the correct adress

            # Sending a reply to client
            received_seq_num = int(message.decode().split(":",1)[0]) #The message format is: (seq_num:msg) so this line is to get the seq_num
            #Search a more efficient way to do this. Perhaps received_seq_num = int(message.decode()[:index(":")]) or something like that
            print("Received seq_num: {}".format(received_seq_num))

            if (received_seq_num == server_seq_num):
                print("Writing to file seq_num: {}".format(received_seq_num))
                f.write(message.decode().split(":", 1)[1])#So it doestn write seq_num:
                #Search a more efficient way to do this. Perhaps received_seq_num = int(message.decode()[:index(":")]) or something like that
                server_seq_num += 1

            #The response will be something like a specific byte meaning ACK and the sequence number
            bytesToSend = received_seq_num.to_bytes(1,"little") #Dont know if it should be little or big
            print("Sending response to seq_num: {}".format(received_seq_num))
            skt.sendto(bytesToSend, address)
            time.sleep(random.uniform(0.3, 1.2)) #To simulate network congestion
            #lost_ack = True
        except socket.timeout:
                    print("Timeout")
                    break


    f.close() """

def main():
    localIP = "127.0.0.1"
    localPort = 8080
    bufferSize = 4096

    # Create a datagram socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.settimeout(8)#Para que cuando me terminen de mandar el archivo termine el programa y se llame a f.close()

    # Bind to address and ip
    UDPServerSocket.bind((localIP, localPort))

    print("UDP server up and listening")

    bytesAddressPair = UDPServerSocket.recvfrom(1) #Receive byte "d" or "u". "d" client wants to download file. "u" client wants to upload file
    message = bytesAddressPair[0]   
    address = bytesAddressPair[1]#Check if im receiving from the correct adress

    if message.decode() == "d":
        protocol.send_file(UDPServerSocket, "../go_back_n/bee_movie_script.txt", address, 1024)
        #print("Client wants to download")
    else:
        protocol.receive_file(UDPServerSocket, "downloadedServer.txt", bufferSize)


if __name__ == "__main__":
    main()