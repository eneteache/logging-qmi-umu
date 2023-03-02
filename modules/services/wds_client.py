import sys, signal, gi

gi.require_version('Qmi', '1.0')
from gi.repository import GLib, Gio, Qmi, GObject
from modules.device.device import Device
from modules import defines

class WDSClient:
    
    num_requests = 0
    global device
    device = Device()

    def __init__(self, qmidev, main_loop) -> None:
        self.qmidev = qmidev
        self.main_loop = main_loop
        device.set_device_clients(device.get_device_clients()+1)
        print("device_clients: ", device.get_device_clients())

    #getters
    def get_qmidev(self):
        return self.qmidev
    
    def get_main_loop(self):
        return self.main_loop
        
    def get_num_requests(self):
        return self.num_requests

    def set_num_requests(self, num_requests):
        self.num_requests = num_requests

    def get_wds_info(self):

        def get_num_requests():
            return self.get_num_requests()
        
        def set_num_requests(num_requests):
            self.set_num_requests(num_requests)

        def device_close_ready(qmidev,result,user_data=None):
            device.set_device_clients(device.get_device_clients()-1)
            try:
                qmidev.close_finish(result)
            except GLib.GError as error:
                sys.stderr.write("Couldn't close QMI device: %s\n" % error.message)
            main_loop.quit()

        def device_close(qmidev):
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

        def get_wds_packet_statistics_ready(wds_client, result, qmidev):
            try:
                output = wds_client.get_packet_statistics_finish(result)
                
                print("WDS TX PACKETS OK:     %s" % output.get_tx_packets_ok())
                print("WDS RX BYTES OK:       %s" % output.get_rx_overflows())
                

                
                
            except GLib.GError as error:
                sys.stderr.write("Couldn't get serving system information: %s\n" % error.message)


            release_client(qmidev, wds_client)

        def allocate_wds_client_ready(qmidev, result, user_data=None):

            try:
                wds_client = qmidev.allocate_client_finish(result)
                
            except GLib.GError as error:
                sys.stderr.write("Couldn't allocate WDS QMI client: %s\n" % error.message)
                device_close(qmidev)
                return

            

            #set all masks
            print(Qmi.WdsPacketStatisticsMaskFlag.TX_PACKETS_OK.value)
            set_num_requests(len(defines.PacketStatisticsMaskFlags))
            for flag in defines.PacketStatisticsMaskFlags:
                pass
                #print(defines.PacketStatisticsMaskFlags[flag])
                # input_value = Qmi.MessageWdsGetPacketStatisticsInput()
                
                # input_value.set_mask(Qmi.WdsPacketStatisticsMaskFlag(flag))
                # wds_client.get_packet_statistics(input_value, 10, None, get_wds_packet_statistics_ready, qmidev)

            

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

        qmidev.allocate_client(Qmi.Service.WDS, Qmi.CID_NONE, 10, None, allocate_wds_client_ready, None)