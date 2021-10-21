import protocol
import socket
import sys

def main():
    serverAddressPort = ("127.0.0.1", 8080)
    bufferSize = 1024

    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPClientSocket.settimeout(1)

    msg = sys.argv[1].encode()
    UDPClientSocket.sendto(msg, serverAddressPort) #byte to tell the server what we want to do

    if sys.argv[1] == "d":
        protocol.receive_file(UDPClientSocket, "downloadedClient.txt", 4096)
    else:
        protocol.send_file(UDPClientSocket, "../go_back_n/bee_movie_script.txt", serverAddressPort, 1024)


if __name__ == "__main__":
    main()