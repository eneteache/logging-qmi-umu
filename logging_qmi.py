import asyncio
from configparser import ConfigParser
import os, sys, signal, gi
import time
from subprocess import Popen, PIPE

from modules.services.client import Client
gi.require_version('Qmi', '1.0')
from gi.repository import GLib, Gio, Qmi

from modules.services.nas_client import NASClient
from modules.services.dms_client import DMSClient
from modules.services.wds_client import WDSClient
import fcntl

from modules  import defines

main_loop = None

def create_usb_list_manual():
    device_list = list()
    try:
        lsusb_out = Popen('lsusb -v', shell=True, bufsize=64, stdin=PIPE, stdout=PIPE, close_fds=True).stdout.read().strip().decode('utf-8')
        usb_devices = lsusb_out.split('%s%s' % (os.linesep, os.linesep))
        for device_categories in usb_devices:
            if not device_categories:
                continue
            categories = device_categories.split(os.linesep)
            device_stuff = categories[0].strip().split()
            bus = device_stuff[1]
            device = device_stuff[3][:-1]
            device_dict = {'bus': bus, 'device': device}
            device_info = ' '.join(device_stuff[6:])
            device_dict['description'] = device_info
            for category in categories:
                if not category:
                    continue
                categoryinfo = category.strip().split()
                if categoryinfo[0] == 'iManufacturer':
                    manufacturer_info = ' '.join(categoryinfo[2:])
                    device_dict['manufacturer'] = manufacturer_info
                if categoryinfo[0] == 'iProduct':
                    device_info = ' '.join(categoryinfo[2:])
                    device_dict['device'] = device_info
            path = '/dev/bus/usb/%s/%s' % (bus, device)
            device_dict['path'] = path

            device_list.append(device_dict)
    except Exception as ex:
        defines.log.error('Failed to list usb devices! Error: %s' % ex)
        return ex
    return device_list

def search_path_manual(dev_sn):
    usb_list = create_usb_list_manual()
    for device in usb_list:
        text = '%s %s %s' % (device['description'], device['manufacturer'], device['device'])
        if dev_sn in text:
            return device['path']
    defines.log.error('Failed to find device!')
    return None

def reset_usb_device_manual(dev_path):
    USBDEVFS_RESET = 21780
    try:
        f = open(dev_path, 'w', os.O_WRONLY)
        fcntl.ioctl(f, USBDEVFS_RESET, 0)
        return
    except Exception as ex:
        defines.log.error('Failed to reset device! Error: %s' % ex)
        return ex

def check_device_manual():

    parser = ConfigParser()
    parser.read('config.ini')
    dev_sn = parser["InfoDevice"]["serial_number"]

    dev_path = search_path_manual(dev_sn)

    if dev_path != None:
        try:
            defines.log.debug("resetting device")
            reset_usb_device_manual(dev_path)
            defines.log.debug('successfully reset %s' % dev_path)
        except Exception as ex:
            sys.exit(-1)
    else:
        defines.log.error("device with sn %s not found" % dev_sn)
        sys.exit(-1)
    

def signal_handler(data):
    main_loop.quit()

def open_ready(qmidev,result,user_data=None):
    try:
        qmidev.open_finish(result)

    except GLib.GError as error:
        defines.log.error("Couldn't open QMI device: %s" % error.message)
        main_loop.quit()
        return
    
    try:
        print(defines.elmundo)
        test_client = Client(qmidev, main_loop, Qmi.Service.DMS)
        test_client.init(check_device_manual)
        print(defines.elmundo)
    except GLib.GError as e:
        print("--ENTRA AQUI con Except--")
        check_device_manual()

    dms_client = DMSClient(qmidev, main_loop)
    nas_client = NASClient(qmidev, main_loop)
    wds_client = WDSClient(qmidev, main_loop)

    #dms_client.reset_dms_device()
    
    dms_client.get_dms_info()
    nas_client.get_nas_serving()
    wds_client.get_wds_info()

    print(defines.elmundo)
    

def new_ready(unused,result,user_data=None):

    try:
        qmidev = Qmi.Device.new_finish(result)
    except GLib.GError as error:
        defines.log.error("Couldn't create QMI device: %s" % error.message)
        check_device_manual()
        main_loop.quit()
        return

    qmidev.open(Qmi.DeviceOpenFlags.PROXY, 10, None, open_ready, None)


if __name__ == "__main__":



    # Process input arguments
    if len(sys.argv) != 2:
        defines.log.error('error: wrong number of arguments')
        defines.log.error('usage: sudo logging_qmi.py <DEVICE>')
        sys.exit(-1)
    
    if os.geteuid() != 0:
        defines.log.error('you need root or sudo permissions to do this')
        sys.exit(-1)


    file = Gio.File.new_for_path(sys.argv[1])
    

    while True:
        Qmi.Device.new (file, None, new_ready, None)
        # Main loop
        main_loop = GLib.MainLoop()
        
        GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGHUP, signal_handler, None)
        GLib.unix_signal_add(GLib.PRIORITY_HIGH, signal.SIGTERM, signal_handler, None)
        try:
            main_loop.run()
        except KeyboardInterrupt:
            pass


        print("sleeping")
        time.sleep(1)