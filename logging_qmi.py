import sys, signal, gi
import time

gi.require_version('Qmi', '1.0')
from gi.repository import GLib, Gio, Qmi
from modules.services.nas.nas_client import NASClient

main_loop = None


def signal_handler(data):
    main_loop.quit()


def device_close_ready(qmidev,result,user_data=None):
    try:
        qmidev.close_finish(result)
    except GLib.GError as error:
        sys.stderr.write("Couldn't close QMI device: %s\n" % error.message)
    main_loop.quit()








def release_client(qmidev, qmiclient):
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

    qmiclient.get_ids(None, 10, None, get_ids_ready, qmidev)


def allocate_DMS_client_ready(qmidev,result,user_data=None):
    try:
        qmi_dms_client = qmidev.allocate_client_finish(result)
    except GLib.GError as error:
        sys.stderr.write("Couldn't allocate DMS QMI client: %s\n" % error.message)
        device_close(qmidev)
        return

    qmi_dms_client.get_capabilities(None, 10, None, get_capabilities_ready, qmidev)



def open_ready(qmidev,result,user_data=None):
    try:
        qmidev.open_finish(result)
    except GLib.GError as error:
        sys.stderr.write("Couldn't open QMI device: %s\n" % error.message)
        main_loop.quit()
        return
    # starting both clients. My expectations that this should run in parallel due to callbacks
    #qmidev.allocate_client(Qmi.Service.DMS, Qmi.CID_NONE, 10, None, allocate_DMS_client_ready, None)

    NASClient.allocate_new_client()
    #qmidev.allocate_client(Qmi.Service.NAS, Qmi.CID_NONE, 10, None, NASClient.allocate_NAS_client_ready, None)

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
