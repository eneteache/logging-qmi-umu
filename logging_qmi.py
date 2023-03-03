from configparser import ConfigParser
import os, sys, signal, gi
import time

gi.require_version('Qmi', '1.0')
from gi.repository import GLib, Gio, Qmi
from modules.services.nas_client import NASClient
from modules.services.dms_client import DMSClient
from modules.services.wds_client import WDSClient
import fcntl

main_loop = None
global device_clients

def reset_usb_device_manual(dev_path):
    USBDEVFS_RESET = 21780
    try:
        f = open(dev_path, 'w', os.O_WRONLY)
        fcntl.ioctl(f, USBDEVFS_RESET, 0)
        return
    except Exception as ex:
        return Exception('Failed to reset device! Error: %s' % ex)
    
def signal_handler(data):
    main_loop.quit()

def open_ready(qmidev,result,user_data=None):
    try:
        qmidev.open_finish(result)
    except GLib.GError as error:
        sys.stderr.write("Couldn't open QMI device: %s\n" % error.message)
        main_loop.quit()
        return
    
    dms_client = DMSClient(qmidev, main_loop, Qmi.Service.DMS)
    #nas_client = NASClient(qmidev, main_loop, Qmi.Service.DMS)
    #wds_client = WDSClient(qmidev, main_loop)

    dms_client.reset_dms_device()
    dms_client.get_dms_info()
    #nas_client.get_nas_serving()
    #wds_client.get_wds_info()

def new_ready(unused,result,user_data=None):
    try:
        qmidev = Qmi.Device.new_finish(result)
    except GLib.GError as error:
        sys.stderr.write("Couldn't create QMI device: %s\n" % error.message)
        main_loop.quit()
        return

    qmidev.open(Qmi.DeviceOpenFlags.PROXY, 10, None, open_ready, None)


if __name__ == "__main__":

    # Process input arguments
    if len(sys.argv) != 2:
        sys.stderr.write('error: wrong number of arguments\n')
        sys.stdout.write('usage: simple-tester-python <DEVICE>\n')
        sys.exit(1)

    parser = ConfigParser()
    parser.read('config.ini')
    dev_path = parser["InfoDevice"]["path"]

    print(dev_path)
    try:
        reset_usb_device_manual(dev_path)
        print('Successfully reset %s' % dev_path)
    except Exception as ex:
        sys.exit(-1)

    file = Gio.File.new_for_path(sys.argv[1])
    Qmi.Device.new (file, None, new_ready, None)

    # Main loop
    main_loop = GLib.MainLoop()
    GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGHUP, signal_handler, None)
    GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGTERM, signal_handler, None)
    try:
        main_loop.run()
    except KeyboardInterrupt:
        pass
