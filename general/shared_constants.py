MAX_BUFFER_SIZE = 1024

MIN_PORT = 1024
MAX_PORT = 65535

MSG_TYPE_SIZE = 1
SEQ_NUM_SIZE = 2
METADATA_SIZE = MSG_TYPE_SIZE + SEQ_NUM_SIZE
MAX_SEQ_NUM = 2**16 - 1

MSG_TYPE_NUM = 67
SYN_TYPE_NUM = 50
OK_TYPE_NUM = 47 # This indicates an accepted SYN request

MAX_CONNECTIONS = 5
UPD_BYTES_PER_FILE_READ = 1000