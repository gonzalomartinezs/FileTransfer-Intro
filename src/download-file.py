import socket
import os
import sys

sys.path.insert(1, '/')  # To fix library includes

import lib.general.shared_constants as constants
from lib.general import client_parser
from lib.general import file_finder
from lib.general.realiable_udp_socket import ReliableUDPSocket


def download_file(arguments, cl_socket):
    msg = "1," + arguments.name + ",0"
    cl_socket.send(msg.encode())

    filesize = int(cl_socket.recv(constants.MAX_BUFFER_SIZE).decode())
    if filesize == 0:
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
        bytes_received = len(received)

        while received != b'':
            file.write(received)
            received = cl_socket.recv(constants.MAX_BUFFER_SIZE)
            bytes_received += len(received)
            print("Downloaded {}/{} bytes".format(bytes_received, filesize))
    except Exception:
        print("Something went wrong while downloading the file.")

    if bytes_received == filesize:
        print("File succesfully downloaded.")
    file.close()


args = client_parser.parse_arguments("download")

if args.mode == "tcp":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
elif args.mode == "gbn":
    client_socket = ReliableUDPSocket(use_goback_n=True)
else:
    client_socket = ReliableUDPSocket(use_goback_n=False)

try:
    client_socket.connect((args.host, args.port))
except ConnectionRefusedError:
    print("The connection has been rejected. The program will close")
    sys.exit(0)

download_file(args, client_socket)

client_socket.close()
