MAX_BUFFER_SIZE = 1024

MIN_PORT = 1024
MAX_PORT = 65535

MSG_TYPE_SIZE = 1
SEQ_NUM_SIZE = 2
METADATA_SIZE = MSG_TYPE_SIZE + SEQ_NUM_SIZE
MAX_SEQ_NUM = 2**16 - 1

MSG_TYPE_NUM = 67
SYN_TYPE_NUM = 50
OK_TYPE_NUM = 47  # This indicates an accepted SYN request


MAX_CONNECTIONS = 5
UPD_BYTES_PER_FILE_READ = 1000

UDP_USE_GO_BACK_N = True

TIME_UNTIL_DISCONNECTION = 3 # Max time in seconds that can pass between received messages until with considered the connection as lost

PING_TIMEOUT = 0.5 # Time in seconds until a ping message is sent for connection testing purpouses
