import socket
from general.server_parser import parse_arguments
from clients_acceptor import ClientsAcceptor


args = parse_arguments()

sv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sv_socket.bind((args.host, args.port))
sv_socket.listen(5)

acceptor = ClientsAcceptor(sv_socket, args)
acceptor.start()

user_input = input("Con 'q' corta\n")
while user_input != "q":
    print("Hay " + str(len(acceptor.clients)) + " clientes")
    user_input = input("Con 'q' corta\n")

acceptor.stop()
sv_socket.shutdown(socket.SHUT_RDWR)
sv_socket.close()
acceptor.join()
