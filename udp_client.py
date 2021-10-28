from general.realiable_udp_socket import ReliableUDPSocket
from general.file_reader import FileReader
import general.shared_constants as constants


def main():
    sckt = ReliableUDPSocket(constants.UDP_USE_GO_BACK_N)
    sckt.connect(('127.0.0.1', 8080))
    reader = FileReader('text_example.txt')
    msg = reader.read_next_section(1000)
    try:
        while True:
            sckt.send(msg)
            msg = reader.read_next_section(constants.UPD_BYTES_PER_FILE_READ)
    except BaseException:
        pass
    sckt.close()


main()
