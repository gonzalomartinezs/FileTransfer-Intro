import sys
sys.path.insert(1, '../')  # To fix library includes

from general.realiable_udp_socket import ReliableUDPSocket
from general.server_parser import parse_arguments
import general.shared_constants as constants


def main(args):
    sckt = ReliableUDPSocket(use_goback_n=True)
    sckt.bind((args.host, args.port))
    sckt.listen(constants.MAX_CONNECTIONS)
    client_sckt = sckt.accept()
    sckt.close()
    while True:
        print(client_sckt.recv().decode(), end='')


main(parse_arguments())
