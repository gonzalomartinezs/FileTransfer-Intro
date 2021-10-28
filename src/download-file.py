import socket
import os
import sys

sys.path.insert(1, '/')  # To fix library includes

import lib.general.shared_constants as constants
from lib.general import client_parser
from lib.general import file_finder
from lib.general.realiable_udp_socket import ReliableUDPSocket



def download_file(arguments, cl_socket):
    msg = "1," + arguments.name
    cl_socket.send(msg.encode())

    response = int(cl_socket.recv(constants.MAX_BUFFER_SIZE).decode())
    if response == 1:
        print("The file does not exist on the server.")
        return

    if file_finder.file_exists(arguments.dest, arguments.name):
        option = "-1"
        while option != "y" and option != "n":
            option = input("The file already exists. "
                           "Do you want to override it? (y/n)")
        if option == "n":
            return

    filepath = os.path.join(arguments.dest, arguments.name)
    try:
        file = open(filepath, "wb")
        received = cl_socket.recv(constants.MAX_BUFFER_SIZE)

        while received != b'':
            file.write(received)
            received = cl_socket.recv(constants.MAX_BUFFER_SIZE)
    except Exception:
        print("Something went wrong while downloading the file.")
    else:
        print("File succesfully downloaded.")
    file.close()


args = client_parser.parse_arguments()
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client_socket = ReliableUDPSocket(use_goback_n=True)

try:
    client_socket.connect((args.host, args.port))
except ConnectionRefusedError:
    print("The connection has been rejected. The program will close")
    sys.exit(0)

download_file(args, client_socket)

client_socket.close()
