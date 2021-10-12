import argparse
from shared_constants import *


def add_optional_arguments(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true",
                       help="increase output verbosity")
    group.add_argument("-q", "--quiet", action="store_true",
                       help="decrease output verbosity")


# Se crea el parser
cl_parser = argparse.ArgumentParser(description="Client-side application")

# Se crean subparsers para los distintos comandos
subparser = cl_parser.add_subparsers(dest="command", help="available commands")
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
add_optional_arguments(upload_parser)
add_optional_arguments(download_parser)

# Pasa los argumentos introducidos a un objeto contenedor
if cl_parser.parse_args().command == "upload-file":
    args = upload_parser.parse_args()
elif cl_parser.parse_args().command == "download-file":
    args = download_parser.parse_args()
else:
    cl_parser.error("Uknown command")

if args.port < CONST_MIN_PORT or args.port > CONST_MAX_PORT:
    cl_parser.error("Port value must be in between [1024-65535]")

print(args.host)
print(args.port)
print(args.storage)
print(args.verbose)
print(args.quiet)
