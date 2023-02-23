import sys, signal, gi

gi.require_version('Qmi', '1.0')
from gi.repository import GLib, Gio, Qmi

class NASClient:
    
    def __init__(self, qmidev, result) -> None:
        self.qmidev = qmidev
        self.result = result

    def get_qmidev(self):
        return self.qmidev

    def device_close_ready(main_loop, qmidev,result,user_data=None):
        try:
            qmidev.close_finish(result)
        except GLib.GError as error:
            sys.stderr.write("Couldn't close QMI device: %s\n" % error.message)
        main_loop.quit()

    def device_close(self, qmidev):
        qmidev.close_async(10, None, self.device_close_ready, None)


    def release_client_ready(self, qmidev,result,user_data=None):
        try:
            qmidev.release_client_finish(result)
        except GLib.GError as error:
            sys.stderr.write("Couldn't release QMI client: %s\n" % error.message)
        self.device_close(qmidev)

    def release_client_ready(self, qmidev, result, user_data=None):
        try:
            qmidev.release_client_finish(result)
        except GLib.GError as error:
            sys.stderr.write("Couldn't release QMI client: %s\n" % error.message)

    def release_client(self, qmidev, qmiclient):
        qmidev.release_client(qmiclient, Qmi.DeviceReleaseClientFlags.RELEASE_CID, 10, None, self.release_client_ready, None)

    def get_nas_serving_system_ready(self, nas_qmiclient,result,qmidev):
        try:
            output = nas_qmiclient.get_serving_system_finish(result)
            output.get_result()

            registration_state, cs_attach_state, ps_attach_state, selected_network, radio_interfaces = output.get_serving_system()
            plmn_mcc, plmn_mnc, plmn_description = output.get_current_plmn()

            print()
            print("NAS registration State: %s" % Qmi.NasRegistrationState.get_string(registration_state))

            #FIXME there are potentially more than one radio interface on the modem so consider that!
            network_mode = ""
            for radioiface in radio_interfaces:
                if network_mode != "":
                    network_mode += ", "
                network_mode += Qmi.NasRadioInterface.get_string(radioiface)

            print("NAS networkmode:       %s" % network_mode)
            print("NAS MCC:               %s" % plmn_mcc)
            print("NAS MNC:               %s" % plmn_mnc)
            print("NAS Description:       %s" % plmn_description)
            print()
            
        except GLib.GError as error:
            sys.stderr.write("Couldn't get serving system information: %s\n" % error.message)

        #FIXME this results in an error -> double free or corruption (fasttop)
        # i dont know how to release both "Clients"
        self.release_client_2(qmidev, nas_qmiclient)

    def allocate_NAS_client_ready(self, result, user_data=None):
        qmidev = self.get_qmidev()
        try:
            qmi_nas_client = qmidev.allocate_client_finish(result)
        except GLib.GError as error:
            sys.stderr.write("Couldn't allocate NAS QMI client: %s\n" % error.message)
            self.device_close(qmidev)
            return
        qmi_nas_client.get_serving_system(None, 10, None, self.get_nas_serving_system_ready, qmidev)

    def allocate_new_client(self):
        self.qmidev.allocate_client(Qmi.Service.NAS, Qmi.CID_NONE, 10, None, self.allocate_NAS_client_ready(self.result), None)