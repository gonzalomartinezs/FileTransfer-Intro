import lib.general.constants as constants
from lib.general.reliable_udp_socket import ReliableUDPSocket
from lib.general.clients_acceptor import ClientsAcceptor
from lib.general.server_parser import parse_arguments
import socket
import sys
sys.path.insert(1, '/')  # To fix library includes


args = parse_arguments()

if args.mode == "tcp":
    sv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
elif args.mode == "gbn":
    sv_socket = ReliableUDPSocket(use_goback_n=True)
else:
    sv_socket = ReliableUDPSocket(use_goback_n=False)

sv_socket.bind((args.host, args.port))
sv_socket.listen(constants.MAX_UNCONFIRMED_CONNECTIONS)

acceptor = ClientsAcceptor(sv_socket, args)
acceptor.start()

user_input = ''
while user_input != "q":
    user_input = input("Para finalizar ingrese la tecla 'q' \n")

acceptor.stop()
if args.mode == "tcp":
    sv_socket.shutdown(socket.SHUT_RDWR)
sv_socket.close()
acceptor.join()
