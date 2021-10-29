from lib.general.reliable_udp_socket import ReliableUDPSocket
from lib.general.file_reader import FileReader
from lib.general import client_parser
import lib.general.constants as constants
import socket
import os
import sys

sys.path.insert(1, '/')  # To fix library includes


def upload_file(arguments, cl_socket):
    filepath = os.path.join(arguments.source, arguments.name)
    filesize = os.path.getsize(filepath)

    msg = "0," + arguments.name + "," + str(filesize)
    cl_socket.sendall(msg.encode())

    response = int(cl_socket.recv(constants.MAX_BUFFER_SIZE).decode())
    if response == 1:
        print("The file already exists on the server.")
        option = "-1"
        while option != "y" and option != "n":
            option = input("Do you want to override it? (y/n)")
        if option == "n":
            cl_socket.sendall("1".encode())
            return
        else:
            cl_socket.sendall("0".encode())

    try:
        file = FileReader(filepath)
    except IOError:
        print("Unable to open file " + filepath + ".")
    else:
        continue_reading = True
        sent = 0
        while continue_reading:
            try:
                bytes_read = file.read_next_section(constants.MAX_BUFFER_SIZE)
                cl_socket.sendall(bytes_read)
                sent += len(bytes_read)
                print("Already sent {}/{} bytes.".format(sent, filesize))
            except EOFError:
                continue_reading = False
                if sent == filesize:
                    print("File successfully uploaded.")
                else:
                    print("An error occurred while uploading the file. Not all"
                          "bytes were sent.")
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
