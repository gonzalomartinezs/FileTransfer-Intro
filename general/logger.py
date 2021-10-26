import logging

ERROR_LEVEL = logging.ERROR
INFO_LEVEL = logging.INFO
DEBUG_LEVEL = logging.DEBUG

logging.basicConfig(
    format='%(%(levelname)s - %(message)s')

logger = logging.getLogger()
