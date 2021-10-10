import socket
from general.file_reader import FileReader

#skt_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#print("cccccc")
#skt_send.connect(("200.63.5.176", 19007))
#print("aaaaa")
skt_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#skt_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#skt_receive.bind((socket.gethostbyname(socket.gethostname()), 19006))
skt_send.sendto(b"Hola crack", ("200.63.5.176", 19007))
#skt_send.send(b"dsasdasdasd")
#print("bbbbb")
#skt_send.sendto(b"Hola crack", ("200.63.5.176", 19006))
#data, addr = skt_receive.recvfrom(1024)
#print("Recibi un mensaje: de", addr, ":", data.decode())

reader = FileReader("bee_movie_script.txt")
should_continue_reading = True

while (should_continue_reading):
    try:
        bytes = reader.read_next_section(4096)
        print(bytes.decode(), end = "")
    except EOFError:
        should_continue_reading = False


