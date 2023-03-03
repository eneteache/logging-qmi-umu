import sys, signal, gi

gi.require_version('Qmi', '1.0')
from gi.repository import GLib, Gio, Qmi

""" QMI Parameters """

DMSService = {"DMS": Qmi.Service.DMS}
NASService = {'NAS': Qmi.Service.NAS}
UIMService = {'UIM': Qmi.Service.UIM}
WDSService = {'WDS': Qmi.Service.WDS}

TypeService = {
    "DMS": Qmi.Service.DMS,
    'NAS': Qmi.Service.NAS,
    'UIM': Qmi.Service.UIM,
    'WDS': Qmi.Service.WDS
}  

PacketStatisticsMaskFlags = {
    'TX_PACKETS_OK': 1,
    'RX_BYTES_OK': 128,
    'TX_OVERFLOWS': 16,
    'RX_PACKETS_OK': 2,
    'TX_PACKETS_DROPPED': 256,
    'RX_OVERFLOWS': 32,
    'TX_PACKETS_ERROR': 4,
    'RX_PACKETS_DROPPED': 512,
    'TX_BYTES_OK': 64,
    'RX_PACKETS_ERROR': 8
}

def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None