import sys, signal, gi
import operator

gi.require_version('Qmi', '1.0')
from gi.repository import GLib, Gio, Qmi, GObject
from modules import defines
from modules.services.client import Client
from modules import defines

class WDSClient(Client):
    
    def __init__(self, qmidev, main_loop) -> None:
        service_type = Qmi.Service.WDS
        super().__init__(qmidev, main_loop, service_type)

    def get_wds_info(self):

        def get_num_requests():
            return self.get_num_requests()
        
        def set_num_requests(num_requests):
            self.set_num_requests(num_requests)
        
        def get_device():
            return self.device

        def device_close_ready(qmidev,result,user_data=None):
            device = get_device()
            device.set_clients(device.get_clients()-1)
            try:
                qmidev.close_finish(result)
            except GLib.GError as error:
                defines.log.error("Couldn't close QMI device: %s\n" % error.message)
            main_loop.quit()

        def device_close(qmidev):
            device = get_device()
            device.set_clients(device.get_clients()-1)
            defines.log.info("num_requests: %i" % get_num_requests())
            defines.log.info("clients: %i" % device.get_clients())
            if (get_num_requests() == 0 and device.get_clients() == 0):
                qmidev.close_async(10, None, device_close_ready, None)

        def release_client_ready(qmidev,result,user_data=None):
            try:
                qmidev.release_client_finish(result)
            except GLib.GError as error:
                defines.log.error("Couldn't release QMI client: %s\n" % error.message)
            device_close(qmidev)

        def release_client(qmidev, qmiclient):
            set_num_requests(get_num_requests()-1)
            if (get_num_requests() == 0):
                qmidev.release_client(qmiclient, Qmi.DeviceReleaseClientFlags.RELEASE_CID, 10, None, release_client_ready, None)

        def get_wds_packet_statistics_ready(wds_client, result, qmidev):
            try:
                output = wds_client.get_packet_statistics_finish(result)
                
                print("")
                print("WDS TX PACKETS OK:       %s" % output.get_tx_packets_ok())
                print("WDS RX_PACKETS_OK:       %s" % output.get_rx_packets_ok())

                print("WDS TX_PACKETS_ERROR:    %s" % output.get_tx_packets_error())
                print("WDS RX_PACKETS_ERROR:    %s" % output.get_rx_packets_error())

                print("WDS TX_OVERFLOWS:        %s" % output.get_tx_overflows())
                print("WDS RX_OVERFLOWS:        %s" % output.get_rx_overflows())
                
                print("WDS TX_BYTES_OK:         %s" % output.get_tx_bytes_ok())
                print("WDS RX_BYTES_OK:         %s" % output.get_rx_bytes_ok())
                
                print("WDS TX_PACKETS_DROPPED:  %s" % output.get_tx_packets_dropped())
                print("WDS RX_PACKETS_DROPPED:  %s" % output.get_rx_packets_dropped())
                print("")

            except GLib.GError as error:
                defines.log.error("Couldn't get packet statistics: %s" % error.message)


            release_client(qmidev, wds_client)

        def allocate_wds_client_ready(qmidev, result, user_data=None):

            try:
                wds_client = qmidev.allocate_client_finish(result)
                
            except GLib.GError as error:
                defines.log.error("Couldn't allocate WDS QMI client: %s\n" % error.message)
                device_close(qmidev)
                return
            
            # print(res)
            new_mask = 0
            for flag in defines.PacketStatisticsMaskFlags:
                new_mask = new_mask + defines.PacketStatisticsMaskFlags[flag]
                #print(new_mask)
                pass
            #print(new_mask)
            
            input_value = Qmi.MessageWdsGetPacketStatisticsInput()
            input_value.set_mask(Qmi.WdsPacketStatisticsMaskFlag(new_mask))

            set_num_requests(get_num_requests()+1)
            wds_client.get_packet_statistics(input_value, 10, None, get_wds_packet_statistics_ready, qmidev)

            

            # input_value.set_mask(Qmi.WdsPacketStatisticsMaskFlag(Qmi.WdsPacketStatisticsMaskFlag.TX_PACKETS_OK))
            # input_value.set_mask(Qmi.WdsPacketStatisticsMaskFlag(Qmi.WdsPacketStatisticsMaskFlag.RX_BYTES_OK))
            # input_value.set_mask(Qmi.WdsPacketStatisticsMaskFlag(Qmi.WdsPacketStatisticsMaskFlag.TX_OVERFLOWS))
            # input_value.set_mask(Qmi.WdsPacketStatisticsMaskFlag(Qmi.WdsPacketStatisticsMaskFlag.RX_PACKETS_OK))
            # input_value.set_mask(Qmi.WdsPacketStatisticsMaskFlag(Qmi.WdsPacketStatisticsMaskFlag.TX_PACKETS_DROPPED))
            # input_value.set_mask(Qmi.WdsPacketStatisticsMaskFlag(Qmi.WdsPacketStatisticsMaskFlag.RX_OVERFLOWS))
            # input_value.set_mask(Qmi.WdsPacketStatisticsMaskFlag(Qmi.WdsPacketStatisticsMaskFlag.TX_PACKETS_ERROR))
            # input_value.set_mask(Qmi.WdsPacketStatisticsMaskFlag(Qmi.WdsPacketStatisticsMaskFlag.RX_PACKETS_DROPPED))
            # input_value.set_mask(Qmi.WdsPacketStatisticsMaskFlag(Qmi.WdsPacketStatisticsMaskFlag.TX_BYTES_OK))
            # input_value.set_mask(Qmi.WdsPacketStatisticsMaskFlag(Qmi.WdsPacketStatisticsMaskFlag.RX_PACKETS_ERROR))

            
            #input_value.unref()
            

        qmidev = self.get_qmidev()
        main_loop = self.get_main_loop()

        qmidev.allocate_client(self.service_type, Qmi.CID_NONE, 10, None, allocate_wds_client_ready, None)