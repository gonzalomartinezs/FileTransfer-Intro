import argparse
from general.shared_constants import *


def __add_optional_arguments(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true",
                       help="increase output verbosity")
    group.add_argument("-q", "--quiet", action="store_true",
                       help="decrease output verbosity")


# Retorna un objeto contenedor con los atributos command, host, port,
# source/dest, name, verbose y quiet.
def parse_arguments():
    # Se crea el parser
    cl_parser = argparse.ArgumentParser(description="Client-side application")

    # Se crean subparsers para los distintos comandos
    subparser = cl_parser.add_subparsers(dest="command",
                                         help="available commands")
    upload_parser = subparser.add_parser("upload-file",
                                         help="Upload a file to the specified server")
    download_parser = subparser.add_parser("download-file",
                                           help="Download a file from the specified server")

    # Argumentos posicionales (obligatorios)
    upload_parser.add_argument("host", help="service IP address")
    upload_parser.add_argument("port", help="service port", type=int)
    upload_parser.add_argument("source",
                               help="source file path")  # podria ser opcional si definimos un default
    upload_parser.add_argument("name", help="file name")

    download_parser.add_argument("host", help="service IP address")
    download_parser.add_argument("port", help="service port", type=int)
    download_parser.add_argument("dest",
                                 help="destination file path")  # podria ser opcional si definimos un default
    download_parser.add_argument("name", help="file name")

    # Argumentos opcionales (llevan '-' adelante)
    __add_optional_arguments(cl_parser)

    args = cl_parser.parse_args()

    if args.port < CONST_MIN_PORT or args.port > CONST_MAX_PORT:
        cl_parser.error("Port value must be in between [1024-65535]")

    return args
