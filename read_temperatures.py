import json
from mitemp.mitemp_bt.mitemp_bt_poller import MiTempBtPoller
from mitemp.mitemp_bt.mitemp_bt_poller import MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY
from btlewrap.bluepy import BluepyBackend
from bluepy.btle import BTLEException
from lywsd03mmc import Lywsd03mmcClient
import datetime

def read_temperatures(config, devices, messages):
    for device in devices:
        mac = config[device].get("device_mac")
        try:
            if mac.startswith('A4:C1:38'):
                client = Lywsd03mmcClient(mac)
            #try:
                sensor_data = client.data
                data = json.dumps({
                "temperature": sensor_data.temperature,
                "humidity": sensor_data.humidity,
                "battery": sensor_data.battery
            })
            else: 
                poller = MiTempBtPoller(mac, BluepyBackend, ble_timeout=config[device].getint("timeout", 10))
                temperature = poller.parameter_value(MI_TEMPERATURE)
                humidity = poller.parameter_value(MI_HUMIDITY)
                battery = poller.parameter_value(MI_BATTERY)

                data = json.dumps({
                "temperature": temperature,
                "humidity": humidity,
                "battery": battery
            })

            print(datetime.datetime.now(), device, " : ", data)
            messages.append({'topic': config[device].get("topic"), 'payload': data, 'retain': config[device].getboolean("retain", False)})
            availability = 'online'
        except BTLEException as e:
            availability = 'offline'
            print(datetime.datetime.now(), "Error connecting to device {0}: {1}".format(device, str(e)))
        except Exception as e:
            availability = 'offline'
            print(datetime.datetime.now(), "Error polling device {0}. Device might be unreachable or offline.".format(device))
        # print(traceback.print_exc())
        finally:
            messages.append({'topic': config[device].get("availability_topic"), 'payload': availability, 'retain': config[device].getboolean("retain", False)})
    return(messages)