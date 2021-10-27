import sys
sys.path.insert(1, '../')  # To fix library includes

from general.realiable_udp_socket import ReliableUDPSocket
from general.file_reader import FileReader
import general.client_parser as client_parser
import general.shared_constants as constants


def main(args):
    sckt = ReliableUDPSocket(constants.UDP_USE_GO_BACK_N)
    sckt.connect(args.host, args.port)
    reader = FileReader(args.source + args.name)
    msg = reader.read_next_section(1000)
    try:
        while True:
            sckt.send(msg)
            msg = reader.read_next_section(constants.UPD_BYTES_PER_FILE_READ)
    except BaseException:
        pass
    sckt.close()


main(client_parser())
