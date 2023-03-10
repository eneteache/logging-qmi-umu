import logging
import sys, signal, gi

import time
gi.require_version('Qmi', '1.0')
from gi.repository import GLib, Gio, Qmi
from modules.services.client import Client
from modules import defines
import json

class DMSClient(Client):

    def __init__(self, qmidev, main_loop) -> None:
        
        service_type = Qmi.Service.DMS
        super().__init__(qmidev, main_loop, service_type)
        
    def get_dms_info(self): 
        
        def get_cid():
            return self.get_cid()
        
        def get_num_requests():
            return self.get_num_requests()
        
        def set_num_requests(num_requests):
            self.set_num_requests(num_requests)
        
        def get_device():
            return self.device

        def device_close_ready(qmidev,result,user_data=None):
            
            try:
                qmidev.close_finish(result)
            except GLib.GError as error:
                defines.log.error("Couldn't close QMI device: %s\n" % error.message)
            main_loop.quit()

        def device_close(qmidev):

            device = get_device()
            device.set_clients(device.get_clients()-1)
            defines.log.info("dms_num_requests: %i" % get_num_requests())
            defines.log.info("dms_clients: %i" % device.get_clients())
            if (get_num_requests() == 0 and device.get_clients() == 0):
                qmidev.close_async(10, None, device_close_ready, None)

        def release_client_ready(qmidev,result,user_data=None):
            try:
                qmidev.release_client_finish(result)
            except GLib.GError as error:
                defines.log.error("Couldn't release QMI client: %s\n" % error.message)
            device_close(qmidev)

        def release_client(qmidev,qmiclient):
            
            set_num_requests(get_num_requests()-1)
            if (get_num_requests() == 0):
                qmidev.release_client(qmiclient, Qmi.DeviceReleaseClientFlags.RELEASE_CID, 10, None, release_client_ready, None)

        def get_ids_ready(qmiclient,result,qmidev):
            
            device = get_device()
            try:
                output = qmiclient.get_ids_finish(result)
                output.get_result()
            except GLib.GError as error:
                defines.log.error("Couldn't query device ids: %s\n" % error.message)
                release_client(qmidev, qmiclient)
                return

            ids = []
            try:
                imei = {"dms_imei": output.get_imei()}
                ids.append(imei)
            except:
                defines.log.error("couldn't query device imei")
                pass

            try:
                imei_software_version = {"dms_imei software version": output.get_imei_software_version()}
                ids.append(imei_software_version)
            except:
                defines.log.error("couldn't query device imei software version")
                pass

            try:
                meid = {"dms_meid": output.get_meid()}
                ids.append(meid)
            except Exception as e:
                #defines.log.error("couldn't query device meid %s" % e)
                pass

            try:
                esn = {"dms_esn": output.get_esn()}
                ids.append(esn)
            except:
                pass
            
            
            device.add_info_json({"ids": ids})
            print(json.dumps(device.get_info_json()))

            release_client(qmidev, qmiclient)

        def get_capabilities_ready(qmiclient,result,qmidev):
            
            try:
                output = qmiclient.get_capabilities_finish(result)
                output.get_result()

                maxtxrate, maxrxrate, dataservicecaps, simcaps, radioifaces = output.get_info()
                
    
                networks = []
                for radioiface in radioifaces:
                    networks.append(Qmi.DmsRadioInterface.get_string(radioiface))

                output_json = {
                    "dms_value_info_max_tx_channel_rate": maxtxrate,
                    "dms_value_info_max_rx_channel_rate": maxrxrate,
                    "dms_value_info_data_service_capability": Qmi.DmsDataServiceCapability.get_string(dataservicecaps),
                    "dms_value_info_sim_capability": Qmi.DmsSimCapability.get_string(simcaps),
                    "dms_value_info_radio_interface_list": networks
                }

                result_json = json.dumps(output_json)
                print(result_json)

            except GLib.GError as error:
                defines.log.error("Couldn't query device capabilities: %s\n" % error.message)

            release_client(qmidev, qmiclient)
            
        def allocate_client_ready(qmidev,result,user_data=None):
            try:
                qmiclient = qmidev.allocate_client_finish(result)
            except GLib.GError as error:
                defines.log.error("Couldn't allocate QMI client: %s\n" % error.message)
                device_close(qmidev)
                return
            
            set_num_requests(get_num_requests()+2)
            qmiclient.get_capabilities(None, 10, None, get_capabilities_ready, qmidev)
            qmiclient.get_ids(None, 10, None, get_ids_ready, qmidev)

        main_loop = self.get_main_loop()
        qmidev = self.get_qmidev()

        qmidev.allocate_client(self.service_type, Qmi.CID_NONE, 10, None, allocate_client_ready, None)

    def reset_dms_device(self):

        def get_num_requests():
            return self.num_requests
        
        def set_num_requests(num_requests):
            self.num_requests = num_requests

        def get_device():
            return self.device

        def device_close_ready(qmidev,result,user_data=None):
            
            try:
                qmidev.close_finish(result)
            except GLib.GError as error:
                defines.log.error("Couldn't close QMI device: %s\n" % error.message)
            main_loop.quit()

        def device_close(qmidev):
            device = get_device()
            device.set_clients(device.get_clients()-1)
            defines.log.info("dms_num_requests: ", get_num_requests())
            defines.log.info("dms_clients: ", device.get_clients())
            if (get_num_requests() == 0 and device.get_clients() == 0):
                qmidev.close_async(10, None, device_close_ready, None)

        def release_client_ready(qmidev,result,user_data=None):
            try:
                qmidev.release_client_finish(result)
            except GLib.GError as error:
                defines.log.error("Couldn't release QMI client: %s\n" % error.message)
            
            defines.log.info("dms device was reseted successfully")

        def release_client(qmidev,qmiclient):
            
            qmidev.release_client(qmiclient, Qmi.DeviceReleaseClientFlags.RELEASE_CID, 10, None, release_client_ready, None)

        def reset_ready(qmiclient,result,qmidev):

            qmiclient.reset_finish(result)
            release_client(qmidev, qmiclient)

        def allocate_client_ready(qmidev,result,user_data=None):
            try:
                qmiclient = qmidev.allocate_client_finish(result)
            except GLib.GError as error:
                defines.log.error("Couldn't allocate QMI client: %s\n" % error.message)
                device_close(qmidev)
                return

            qmiclient.reset(None, 10, None, reset_ready, qmidev)
            

        main_loop = self.get_main_loop()
        qmidev = self.get_qmidev()


        qmidev.allocate_client(Qmi.Service.DMS, Qmi.CID_NONE, 10, None, allocate_client_ready, None)

