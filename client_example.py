from general.realiable_udp_socket import ReliableUDPSocket
from general.file_reader import FileReader

def main():
    sckt = ReliableUDPSocket(True)
    sckt.connect(('127.0.0.1', 8080))
    reader = FileReader('text_example.txt')
    msg = reader.read_next_section(1000)
    try:
        while True:
            sckt.send(msg)
            msg = reader.read_next_section(1000)
    except:
        pass
    sckt.close()


main()
