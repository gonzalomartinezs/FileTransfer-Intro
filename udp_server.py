from src.lib.general.realiable_udp_socket import ReliableUDPSocket, \
    general as constants


def main():
    sckt = ReliableUDPSocket(use_goback_n=True)
    sckt.bind(('127.0.0.1', 8080))
    sckt.listen(constants.MAX_CONNECTIONS)
    client_sckt, _ = sckt.accept()
    sckt.close()
    r = client_sckt.recv(1024)
    while r != b'':
        print(r.decode(), end='')
        r = client_sckt.recv(1024)
    client_sckt.close()

main()
