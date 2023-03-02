import sys, signal, gi

gi.require_version('Qmi', '1.0')
from gi.repository import GLib, Gio, Qmi
from modules.device.device import Device
dir(GLib)
class DMSClient:

    num_requests = 0
    global device
    device = Device()

    def __init__(self, qmidev, main_loop) -> None:
        self.qmidev = qmidev
        self.main_loop = main_loop

        device.set_device_clients(device.get_device_clients()+1)
        print("new device_clients: ", device.get_device_clients(), "\n")

    #getters
    def get_qmidev(self):
        return self.qmidev
    def get_main_loop(self):
        return self.main_loop
    
    def get_num_requests(self):
        return self.num_requests

    def set_num_requests(self, num_requests):
        self.num_requests = num_requests

    def get_dms_info(self):

        def get_num_requests():
            return self.get_num_requests()
        
        def set_num_requests(num_requests):
            self.set_num_requests(num_requests)
        
        def device_close_ready(qmidev,result,user_data=None):
            
            try:
                qmidev.close_finish(result)
            except GLib.GError as error:
                sys.stderr.write("Couldn't close QMI device: %s\n" % error.message)
            main_loop.quit()


        def device_close(qmidev):
            device.set_device_clients(device.get_device_clients()-1)
            print("dms_num_requests: ", get_num_requests())
            print("dms_device_clients: ", device.get_device_clients())
            if (get_num_requests() == 0 and device.get_device_clients() == 0):
                qmidev.close_async(10, None, device_close_ready, None)


        def release_client_ready(qmidev,result,user_data=None):
            try:
                qmidev.release_client_finish(result)
            except GLib.GError as error:
                sys.stderr.write("Couldn't release QMI client: %s\n" % error.message)
            device_close(qmidev)

        def release_client(qmidev,qmiclient):
            
            set_num_requests(get_num_requests()-1)
            if (get_num_requests() == 0):
                qmidev.release_client(qmiclient, Qmi.DeviceReleaseClientFlags.RELEASE_CID, 10, None, release_client_ready, None)


        def get_ids_ready(qmiclient,result,qmidev):
            
            
            try:
                output = qmiclient.get_ids_finish(result)
                output.get_result()
            except GLib.GError as error:
                sys.stderr.write("Couldn't query device ids: %s\n" % error.message)
                release_client(qmidev, qmiclient)
                return

            try:
                imei = output.get_imei()
                print("imei:                  %s" % imei)
            except:
                pass

            try:
                imei_software_version = output.get_imei_software_version()
                print("imei software version: %s" % imei_software_version)
            except:
                pass

            try:
                meid = output.get_meid()
                print("meid:                  %s" % meid)
            except:
                pass

            try:
                esn = output.get_esn()
                print("esn:                   %s" % esn)
            except:
                pass
            
            
            release_client(qmidev, qmiclient)


        def get_capabilities_ready(qmiclient,result,qmidev):
            
            try:
                output = qmiclient.get_capabilities_finish(result)
                output.get_result()

                maxtxrate, maxrxrate, dataservicecaps, simcaps, radioifaces = output.get_info()
                print("max tx channel rate:   %u" % maxtxrate)
                print("max rx channel rate:   %u" % maxrxrate)
                print("data service:          %s" % Qmi.DmsDataServiceCapability.get_string(dataservicecaps))
                print("sim:                   %s" % Qmi.DmsSimCapability.get_string(simcaps))
                networks = ""
                for radioiface in radioifaces:
                    if networks != "":
                        networks += ", "
                    networks += Qmi.DmsRadioInterface.get_string(radioiface)
                print("networks:              %s" % networks)

            except GLib.GError as error:
                sys.stderr.write("Couldn't query device capabilities: %s\n" % error.message)

            release_client(qmidev, qmiclient)
            


        def allocate_client_ready(qmidev,result,user_data=None):
            try:
                qmiclient = qmidev.allocate_client_finish(result)
            except GLib.GError as error:
                sys.stderr.write("Couldn't allocate QMI client: %s\n" % error.message)
                device_close(qmidev)
                return

            set_num_requests(get_num_requests()+2)
            qmiclient.get_capabilities(None, 10, None, get_capabilities_ready, qmidev)
            qmiclient.get_ids(None, 10, None, get_ids_ready, qmidev)

        qmidev = self.get_qmidev()
        main_loop = self.get_main_loop()

        qmidev.allocate_client(Qmi.Service.DMS, Qmi.CID_NONE, 10, None, allocate_client_ready, None)
