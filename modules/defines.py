import sys, signal, gi

gi.require_version('Qmi', '1.0')
from gi.repository import GLib, Gio, Qmi

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