import sys, signal, gi



gi.require_version('Qmi', '1.0')
from gi.repository import GLib, Gio, Qmi
from modules.services.client import Client

class NASClient(Client):
    
    def __init__(self, qmidev, main_loop) -> None:
        service_type = Qmi.Service.NAS
        super().__init__(qmidev, main_loop, service_type)

    def get_nas_serving(self):

        def get_num_requests():
            return self.get_num_requests()
        
        def set_num_requests(num_requests):
            self.set_num_requests(num_requests)
        
        def get_device():
            return self.device

        def device_close_ready(qmidev,result,user_data=None):
            device = get_device()
            device.set_device_clients(device.get_device_clients()-1)
            try:
                qmidev.close_finish(result)
            except GLib.GError as error:
                sys.stderr.write("Couldn't close QMI device: %s\n" % error.message)
            main_loop.quit()

        def device_close(qmidev):
            device = get_device()
            device.set_device_clients(device.get_device_clients()-1)
            print("num_requests: ", get_num_requests())
            print("device_clients: ", device.get_device_clients())
            if (get_num_requests() == 0 and device.get_device_clients() == 0):
                qmidev.close_async(10, None, device_close_ready, None)

        def release_client_ready(qmidev,result,user_data=None):
            try:
                qmidev.release_client_finish(result)
            except GLib.GError as error:
                sys.stderr.write("Couldn't release QMI client: %s\n" % error.message)
            device_close(qmidev)

        def release_client(qmidev, qmiclient):
            set_num_requests(get_num_requests()-1)
            if (get_num_requests() == 0):
                qmidev.release_client(qmiclient, Qmi.DeviceReleaseClientFlags.RELEASE_CID, 10, None, release_client_ready, None)

        def get_nas_serving_system_ready(nas_qmiclient,result,qmidev):
            try:
                output = nas_qmiclient.get_serving_system_finish(result)
                
                output.get_result()

                registration_state, cs_attach_state, ps_attach_state, selected_network, radio_interfaces = output.get_serving_system()
                plmn_mcc, plmn_mnc, plmn_description = output.get_current_plmn()

                print()
                print("NAS registration State:  %s" % Qmi.NasRegistrationState.get_string(registration_state))

                #FIXME there are potentially more than one radio interface on the modem so consider that!
                network_mode = ""
                for radioiface in radio_interfaces:
                    if network_mode != "":
                        network_mode += ", "
                    network_mode += Qmi.NasRadioInterface.get_string(radioiface)

                print("NAS networkmode:         %s" % network_mode)
                print("NAS MCC:                 %s" % plmn_mcc)
                print("NAS MNC:                 %s" % plmn_mnc)
                print("NAS Description:         %s" % plmn_description)
                print()
                
            except GLib.GError as error:
                sys.stderr.write("Couldn't get serving system information: %s\n" % error.message)

            release_client(qmidev, nas_qmiclient)

        def allocate_NAS_client_ready(qmidev, result, user_data=None):

            try:
                qmi_nas_client = qmidev.allocate_client_finish(result)
                
            except GLib.GError as error:
                sys.stderr.write("Couldn't allocate NAS QMI client: %s\n" % error.message)
                device_close(qmidev)
                return
            
            
            set_num_requests(get_num_requests()+1)
            qmi_nas_client.get_serving_system(None, 10, None, get_nas_serving_system_ready, qmidev)
            

        qmidev = self.get_qmidev()
        main_loop = self.get_main_loop()

        qmidev.allocate_client(self.service_type, Qmi.CID_NONE, 10, None, allocate_NAS_client_ready, None)
