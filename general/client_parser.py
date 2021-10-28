import argparse
import general.shared_constants as constants
from general.file_finder import dir_exists


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
    upload_parser = subparser.add_parser(
        "upload-file", help="Upload a file to the specified server")
    download_parser = subparser.add_parser(
        "download-file", help="Download a file from the specified server")

    # Argumentos posicionales (obligatorios)
    upload_parser.add_argument("-H", dest="host", help="service IP address", required=True)
    upload_parser.add_argument("-p", dest="port", help="service port", type=int, required=True)
    upload_parser.add_argument("-s", dest="source", help="source file path", default='./')
    upload_parser.add_argument("-n", dest="name", help="file name", required=True)

    download_parser.add_argument("-H", dest="host", help="service IP address", required=True)
    download_parser.add_argument("-p", dest="port", help="service port", type=int, required=True)
    download_parser.add_argument("-d", dest="dest", help="destination file path", default='./')
    download_parser.add_argument("-n", dest="name", help="file name", required=True)

    # Argumentos opcionales
    __add_optional_arguments(cl_parser)

    args = cl_parser.parse_args()

    if args.port < constants.MIN_PORT or args.port > constants.MAX_PORT:
        cl_parser.error("Port value must be in between [1024-65535]")

    if args.command == "upload-file" and not dir_exists(args.source):
        cl_parser.error("Invalid source path.")
    elif args.command == "download-file" and not dir_exists(args.dest):
        cl_parser.error("Invalid dest path.")

    return args
