import argparse
from lib.general.constants import *
from lib.general.file_finder import dir_exists


# Retorna un objeto contenedor con los atributos command, host, port, storage,
# verbose y quiet
def parse_arguments():
    # Se crea el parser
    sv_parser = argparse.ArgumentParser(
        description="Start the server and set it "
                    "ready to receive connections.")

    # Argumentos posicionales (obligatorios)
    sv_parser.add_argument(
        "-H",
        dest='host',
        help="service IP address",
        required=True)
    sv_parser.add_argument(
        "-p",
        dest='port',
        help="service port",
        type=int,
        required=True)
    sv_parser.add_argument(
        "-s",
        dest='storage',
        help="storage dir path",
        type=str,
        default='./')
    sv_parser.add_argument("-m", dest="mode", help="socket type used "
                                                   "TCP, GBN: UDP GoBackN"
                                                   ", SW: UDP Stop&Wait",
                           choices=["tcp", "gbn", "sw"], default="tcp")

    # Argumentos opcionales
    group = sv_parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true",
                       help="increase output verbosity")
    group.add_argument("-q", "--quiet", action="store_true",
                       help="decrease output verbosity")

    # Pasa los argumentos introducidos a un objeto contenedor
    args = sv_parser.parse_args()

    if args.port < MIN_PORT or args.port > MAX_PORT:
        sv_parser.error("Port value must be in between [1024-65535]")

    if not dir_exists(args.storage):
        sv_parser.error("Invalid storage path.")

    return args
