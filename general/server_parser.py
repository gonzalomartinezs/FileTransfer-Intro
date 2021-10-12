import argparse

# Se crea el parser
parser = argparse.ArgumentParser(description="Start the server and set it "
                                             "ready to receive connections.")

# Argumentos posicionales (obligatorios)
parser.add_argument("host", help="service IP address")
parser.add_argument("port", help="service port")
parser.add_argument("storage", help="storage dir path") # podria ser opcional si definimos un default

# Argumentos opcionales (llevan '-' adelante)
group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", action="store_true",
                   help="increase output verbosity")
group.add_argument("-q", "--quiet", action="store_true",
                   help="decrease output verbosity")

# Pasa los argumentos introducidos a un objeto contenedor
args = parser.parse_args()

print(args.host)
print(args.port)
print(args.storage)
print(args.verbose)
print(args.quiet)
