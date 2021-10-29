MAX_BUFFER_SIZE = 1024

MIN_PORT = 1024
MAX_PORT = 65535

MSG_TYPE_SIZE = 1
SEQ_NUM_SIZE = 2
METADATA_SIZE = MSG_TYPE_SIZE + SEQ_NUM_SIZE
MAX_SEQ_NUM = 2**16 - 1
MAX_UDP_PACKET_SIZE = MAX_BUFFER_SIZE + METADATA_SIZE

MSG_TYPE_NUM = 67
ACK_TYPE_NUM = 130
SYN_TYPE_NUM = 50
OK_TYPE_NUM = 47  # This indicates an accepted SYN request

PACKET_TIMEOUT = 30  # in ms

MAX_UNCONFIRMED_CONNECTIONS = 5
UPD_BYTES_PER_FILE_READ = 1024

UDP_USE_GO_BACK_N = True

TIME_UNTIL_DISCONNECTION = 3 # Max time in seconds that can pass between received messages until with considered the connection as lost

PING_TIMEOUT = 0.5 # Time in seconds until a ping message is sent for connection testing purpouses

PACKET_QUEUE_SIZE = 20 # Maximum amount of packets that can be received simultanously

GBN_WINDOW_SIZE = 15 # The size of the window in GBN

CONNECT_TIMEOUT = 2 # The time in seconds until the connect method throws an error because no connection was established