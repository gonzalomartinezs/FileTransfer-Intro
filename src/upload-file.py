import socket
import os
import sys

sys.path.insert(1, '/')  # To fix library includes

import lib.general.shared_constants as constants
from lib.general import client_parser
from lib.general.file_reader import FileReader
from lib.general.realiable_udp_socket import ReliableUDPSocket


def upload_file(arguments, cl_socket):
    msg = "0," + arguments.name
    cl_socket.send(msg.encode())

    response = int(cl_socket.recv(constants.MAX_BUFFER_SIZE).decode())
    if response == 1:
        print("The file already exists on the server.")
        option = "-1"
        while option != "y" and option != "n":
            option = input("Do you want to override it? (y/n)")
        if option == "n":
            cl_socket.send("1".encode())
            return
        else:
            cl_socket.send("0".encode())

    filepath = os.path.join(arguments.source, arguments.name)
    try:
        file = FileReader(filepath)
    except IOError:
        print("Unable to open file " + filepath + ".")
    else:
        continue_reading = True
        while continue_reading:
            try:
                bytes_read = file.read_next_section(1000)
                cl_socket.send(bytes_read)
            except EOFError:
                continue_reading = False
                print("File successfully uploaded.")
            except BaseException:
                continue_reading = False
                print("An error occurred while uploading the file.")
        file.close()


args = client_parser.parse_arguments("upload")

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

upload_file(args, client_socket)

client_socket.close()
