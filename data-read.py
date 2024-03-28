#!/usr/bin/python3

import sys
from mitemp.mitemp_bt.mitemp_bt_poller import MiTempBtPoller
from mitemp.mitemp_bt.mitemp_bt_poller import MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY
from btlewrap.bluepy import BluepyBackend
from bluepy.btle import BTLEException
import paho.mqtt.publish as publish
import traceback
import configparser
import os
import json
import datetime
from lywsd03mmc import Lywsd03mmcClient

workdir = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read("{0}/devices.ini".format(workdir))

devices = config.sections()

# Averages
averages = configparser.ConfigParser()
averages.read("{0}/averages.ini".format(workdir))

messages = []

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
    print(datetime.datetime.now(), device, " : ", messages)

sys.exit()
# Init MQTT
mqtt_config = configparser.ConfigParser()
mqtt_config.read("{0}/mqtt.ini".format(workdir))
mqtt_broker_cfg = mqtt_config["broker"]

try:
    auth = None
    mqtt_username = mqtt_broker_cfg.get("username")
    mqtt_password = mqtt_broker_cfg.get("password")

    if mqtt_username:
        auth = {"username": mqtt_username, "password": mqtt_password}

    publish.multiple(messages, hostname=mqtt_broker_cfg.get("host"), port=mqtt_broker_cfg.getint("port"), client_id=mqtt_broker_cfg.get("client"), auth=auth)
except Exception as ex:
    print(datetime.datetime.now(), "Error publishing to MQTT: {0}".format(str(ex)))

with open("{0}/averages.ini".format(workdir), "w") as averages_file:
    averages.write(averages_file)
