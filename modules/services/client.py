import sys, signal, gi
from configparser import ConfigParser
import time
gi.require_version('Qmi', '1.0')
from gi.repository import GLib, Gio, Qmi
from modules.device.device import Device
from modules import defines

class Client():
    
    num_requests = 0

    def __init__(self, qmidev, main_loop, service_type) -> None:
        
        self.log = defines.log

        self.cid = 0
        self.qmidev = qmidev
        self.main_loop = main_loop
        self.service_type = service_type
        
        self.device = Device()
        self.device.set_clients(self.device.get_clients()+1)
        
        self.log.info("new {} client - ID: {} ".format(Qmi.service_get_string(self.service_type).upper(), self.device.get_clients()))

    #getters
    def get_cid(self):
        return self.cid
    
    def set_cid(self, cid):
        self.cid = cid

    def get_device(self):
        return self.device

    def get_qmidev(self):
        return self.qmidev
    
    def get_main_loop(self):
        return self.main_loop
    
    def get_num_requests(self):
        return self.num_requests

    def set_num_requests(self, num_requests):
        self.num_requests = num_requests
        

    def init(self, check_device_manual):


        def sub_clients():
            self.device.set_clients(self.device.get_clients()-1)
        def device_close_ready(qmidev,result,user_data=None):
            
            try:
                qmidev.close_finish(result)
            except GLib.GError as error:
                defines.log.error("Couldn't close QMI device: %s\n" % error.message)
            main_loop.quit()

        def device_close(qmidev):

            qmidev.close_async(10, None, device_close_ready, None)

        def release_client_ready(qmidev,result,user_data=None):
            try:
                qmidev.release_client_finish(result)
            except GLib.GError as error:
                defines.log.error("Couldn't release QMI client: %s\n" % error.message)

            sub_clients()

        def release_client(qmidev,qmiclient):
            
            qmidev.release_client(qmiclient, Qmi.DeviceReleaseClientFlags.NONE, 10, None, release_client_ready, None)

        def set_cid(cid):
            self.cid = cid
        
        def device_close_ready(qmidev, result, user_data=None):
            try:
                qmidev.close_finish(result)
            except GLib.GError as error:
                defines.log.error("Couldn't close QMI device: %s\n" % error.message)
            main_loop.quit()

        def allocate_client_ready(qmidev,result,user_data=None):
            
            try:
                qmiclient = qmidev.allocate_client_finish(result)
            except GLib.GError as error:
                defines.log.error("Couldn't allocate QMI client: %s\n" % error.message)
                
                user_data()
                #device_close(qmidev)
                return error

            if self.cid != qmiclient.get_cid():
                cid = qmiclient.get_cid()
                #defines.log.info("--- Init CID: {} - {}".format(cid, Qmi.service_get_string(service_type)))
                set_cid(cid)
            defines.elmundo = 2
            release_client(qmidev, qmiclient)

        service_type = self.service_type
        main_loop = self.get_main_loop()
        qmidev = self.get_qmidev()

        qmidev.allocate_client(self.service_type, Qmi.CID_NONE, 10, None, allocate_client_ready, check_device_manual)
