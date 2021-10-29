import argparse
from lib.general.constants import *
from lib.general.file_finder import dir_exists


def __add_optional_arguments(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true",
                       help="increase output verbosity")
    group.add_argument("-q", "--quiet", action="store_true",
                       help="decrease output verbosity")


# Retorna un objeto contenedor con los atributos host, port,
# source/dest, name, verbose y quiet.
def parse_arguments(mode):
    descript = "Client-side application"
    if mode == "download":
        descript = descript + " for downloading files."
    elif mode == "upload":
        descript = descript + " for uploading files."

    # Se crea el parser
    cl_parser = argparse.ArgumentParser(description=descript)

    # Argumentos posicionales (obligatorios)
    cl_parser.add_argument(
        "-H",
        dest="host",
        help="service IP address",
        required=True)
    cl_parser.add_argument(
        "-p",
        dest="port",
        help="service port",
        type=int,
        required=True)

    if mode == "download":
        cl_parser.add_argument(
            "-d",
            dest="dest",
            help="destination file path",
            default='./')
    elif mode == "upload":
        cl_parser.add_argument(
            "-s",
            dest="source",
            help="source file path",
            default='./')

    cl_parser.add_argument("-n", dest="name", help="file name", required=True)
    cl_parser.add_argument("-m", dest="mode", help="socket type used "
                                                   "TCP, GBN: UDP GoBackN"
                                                   ", SW: UDP Stop&Wait",
                           choices=["tcp", "gbn", "sw"], default="tcp")

    # Argumentos opcionales
    __add_optional_arguments(cl_parser)

    args = cl_parser.parse_args()

    if args.port < MIN_PORT or args.port > MAX_PORT:
        cl_parser.error("Port value must be in between [1024-65535]")

    if mode == "upload" and not dir_exists(args.source):
        cl_parser.error("Invalid source path.")
    elif mode == "download" and not dir_exists(args.dest):
        cl_parser.error("Invalid dest path.")

    return args
