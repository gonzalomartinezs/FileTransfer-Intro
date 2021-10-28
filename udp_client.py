from src.lib.general.realiable_udp_socket import ReliableUDPSocket, \
    general as constants
from src.lib.general.file_reader import FileReader


def main():
    sckt = ReliableUDPSocket(constants.UDP_USE_GO_BACK_N)
    sckt.connect(('127.0.0.1', 8080))
    reader = FileReader('text_example.txt')
    msg = reader.read_next_section(1000)
    r = sckt.recv(1024)
    try:
        while r != b'':
            msg = reader.read_next_section(constants.UPD_BYTES_PER_FILE_READ)
            r = sckt.recv(1024)
    except BaseException:
        pass
    sckt.close()


main()
