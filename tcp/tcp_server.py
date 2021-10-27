#import socket
import sys
sys.path.insert(1, '../')  # To fix library includes

from general.server_parser import parse_arguments
from clients_acceptor import ClientsAcceptor
import general.shared_constants as constants
from general.realiable_udp_socket import ReliableUDPSocket

args = parse_arguments()

#sv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sv_socket = ReliableUDPSocket(use_goback_n=False)
sv_socket.bind((args.host, args.port))
sv_socket.listen(constants.MAX_CONNECTIONS)

acceptor = ClientsAcceptor(sv_socket, args)
acceptor.start()

user_input = ''
while user_input != "q":
    print("Hay " + str(len(acceptor.clients)) + " clientes")
    user_input = input("Para finalizar ingrese la tecla 'q' \n")

acceptor.stop()
<<<<<<< HEAD
#sv_socket.shutdown(socket.SHUT_RDWR)
=======

if len(acceptor.clients) > 0:
    sv_socket.shutdown(socket.SHUT_RDWR)
>>>>>>> 61a91f14aa4ce4384e56755fbdf64a992b463c4e
sv_socket.close()
acceptor.join()
