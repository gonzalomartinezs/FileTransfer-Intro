import argparse


# Se crea el parser
sv_parser = argparse.ArgumentParser(description="Start the server and set it "
                                                "ready to receive connections.")

# Argumentos posicionales (obligatorios)
sv_parser.add_argument("host", help="service IP address")
sv_parser.add_argument("port", help="service port", type=int)
sv_parser.add_argument("storage",
                       help="storage dir path")  # podria ser opcional si definimos un default

# Argumentos opcionales (llevan '-' adelante)
group = sv_parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", action="store_true",
                   help="increase output verbosity")
group.add_argument("-q", "--quiet", action="store_true",
                   help="decrease output verbosity")

# Pasa los argumentos introducidos a un objeto contenedor
args = sv_parser.parse_args()

if args.port < 1024 or args.port > 65535:
    sv_parser.error("Port value must be in between [1024-65535]")

print(args.host)
print(args.port)
print(args.storage)
print(args.verbose)
print(args.quiet)
