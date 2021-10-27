#import socket
import os
import sys
sys.path.insert(1, '../')  # To fix library includes

import general.shared_constants as constants
import general.client_parser as client_parser
import general.file_finder as file_finder
from general.file_reader import FileReader
from general.realiable_udp_socket import ReliableUDPSocket


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

    try:
        filepath = os.path.join(arguments.source, arguments.name)
        file = FileReader(filepath)
    except IOError:
        print("Unable to open file {}.".format(filepath)) #TODO wtf is this
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
        cl_socket.send(b'FIN')
        file.close()


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
    file = open(filepath, "wb")
    received = cl_socket.recv(constants.MAX_BUFFER_SIZE)

    while received != b'FIN':
        file.write(received)
        received = cl_socket.recv(constants.MAX_BUFFER_SIZE)

    file.close()


args = client_parser.parse_arguments()
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((args.host, args.port))
except ConnectionRefusedError:
    print("The connection has been rejected. The program will close")
    sys.exit(0)

if args.command == "upload-file":
    upload_file(args, client_socket)
if args.command == "download-file":
    download_file(args, client_socket)
else:
    print("Invalid command. Please insert either download-file or upload-file")

client_socket.close()
