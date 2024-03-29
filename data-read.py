#!/usr/bin/python3

import sys

import paho.mqtt.publish as publish
import traceback
import configparser
import os
import json
import datetime

from read_temperatures import read_temperatures
import ha_config

workdir = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read("{0}/devices.ini".format(workdir))

devices = config.sections()

# Averages
averages = configparser.ConfigParser()
averages.read("{0}/averages.ini".format(workdir))

messages = []

if len(sys.argv)==2:
    if sys.argv[1]=="-R":
        # Register to Home Assistant
        messages=ha_config.create_ha_config(config,devices)
    if sys.argv[1]=="-U":
        # Unregister from Home Asssistant
        messages=ha_config.delete_ha_config(config,devices)
else:
    messages=read_temperatures(config, devices, messages)
    
print(messages)
#sys.exit()
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


