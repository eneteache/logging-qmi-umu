from configparser import ConfigParser
import logging
import sys, signal, gi


""" Config Logging """

parser = ConfigParser()
parser.read('config.ini')
logfile = parser["LoggingConfig"]["path"]
debug_level = parser["LoggingConfig"]["debug_level"]

log_file_handler_format = logging.Formatter('%(asctime)s - %(levelname)s - [line %(lineno)d in %(filename)s] %(message)s ')

log_file_handler = logging.FileHandler(filename=logfile, encoding='utf-8')
log_file_handler.setLevel(debug_level)
log_file_handler.setFormatter(log_file_handler_format)
log_file_handler.mode = 'w'

infoHandler = logging.StreamHandler(sys.stdout)
infoHandler.setLevel(logging.INFO)
infoHandler.setFormatter(log_file_handler_format)

errorHandler = logging.StreamHandler(sys.stderr)
errorHandler.setLevel(logging.ERROR)
errorHandler.setFormatter(log_file_handler_format)

log = logging.getLogger("clients")
log.setLevel(logging.DEBUG)
log.addHandler(infoHandler)
#log.addHandler(errorHandler)
log.addHandler(log_file_handler)

elmundo = 1

""" QMI Parameters """

PacketStatisticsMaskFlags = {
    'TX_PACKETS_OK': 1,
    'RX_PACKETS_OK': 2,
    'TX_PACKETS_ERROR': 4,
    'RX_PACKETS_ERROR': 8,
    'TX_OVERFLOWS': 16,
    'RX_OVERFLOWS': 32,
    'TX_BYTES_OK': 64,
    'RX_BYTES_OK': 128,
    'TX_PACKETS_DROPPED': 256,
    'RX_PACKETS_DROPPED': 512   
}

def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None