from general.realiable_udp_socket import ReliableUDPSocket

def main():
    sckt = ReliableUDPSocket(use_goback_n=True)
    sckt.bind(('127.0.0.1', 8080))
    sckt.listen(10)
    client_sckt = sckt.accept()
    sckt.close()
    while True:
        print(client_sckt.recv().decode(), end='')

main()
