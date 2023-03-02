import sys, signal, gi

gi.require_version('Qmi', '1.0')
from gi.repository import GLib, Gio, Qmi
from modules.device.device import Device
class Client():
    
    num_requests = 0

    def __init__(self, qmidev, main_loop, service_type) -> None:
        self.cid = 0
        self.qmidev = qmidev
        self.main_loop = main_loop
        self.service_type = service_type

        self.device = device = Device()
        device.set_device_clients(device.get_device_clients()+1)
        self.init()

        print("new device - CID:", self.cid)

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

    def init(self):
        
        def set_cid(cid):
            self.cid = cid
        
        def device_close_ready(qmidev, result, user_data=None):
            try:
                qmidev.close_finish(result)
            except GLib.GError as error:
                sys.stderr.write("Couldn't close QMI device: %s\n" % error.message)
            main_loop.quit()

        def allocate_client_ready(qmidev,result,user_data=None):
            try:
                qmiclient = qmidev.allocate_client_finish(result)
            except GLib.GError as error:
                sys.stderr.write("Couldn't allocate QMI client: %s\n" % error.message)
                qmidev.close_async(10, None, device_close_ready, None)
                return

            cid = qmiclient.get_cid()
            print("--- CID: ", cid)
            set_cid(cid)
            
            #release_client(qmidev, qmiclient)


        main_loop = self.get_main_loop()
        qmidev = self.get_qmidev()
        qmidev.allocate_client(self.service_type, Qmi.CID_NONE, 10, None, allocate_client_ready, None)


    
