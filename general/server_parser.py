import argparse
import general.shared_constants as constants
from general.file_finder import dir_exists


# Retorna un objeto contenedor con los atributos command, host, port, storage,
# verbose y quiet
def parse_arguments():
    # Se crea el parser
    sv_parser = argparse.ArgumentParser(
        description="Start the server and set it "
                    "ready to receive connections.")

    # Argumentos posicionales (obligatorios)
    sv_parser.add_argument("-H", dest='host', help="service IP address", type=str, default='127.0.0.1')
    sv_parser.add_argument("-p", dest='port', help="service port", type=int, default=8080)
    # podria ser opcional si definimos un default
    sv_parser.add_argument("-s", dest='storage', help="storage dir path", type=str, default='./')

    # Argumentos opcionales (llevan '-' adelante)
    group = sv_parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true",
                       help="increase output verbosity")
    group.add_argument("-q", "--quiet", action="store_true",
                       help="decrease output verbosity")

    # Pasa los argumentos introducidos a un objeto contenedor
    args = sv_parser.parse_args()

    if args.port < constants.MIN_PORT or args.port > constants.MAX_PORT:
        sv_parser.error("Port value must be in between [1024-65535]")

    if not dir_exists(args.storage):
        sv_parser.error("Invalid storage path.")

    return args
