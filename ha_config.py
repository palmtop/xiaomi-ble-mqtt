import configparser
import json

def create_ha_config(config:configparser.ConfigParser,devices):
    messages = []
    for device in devices:
        #temperature
        payload = {
            "name": device + " Temperature",
            "state_topic": config[device].get('topic'),
            "unit_of_measurement": "°C",
            "device_class":"temperature",
            "value_template": '{{ value_json.temperature }}',
            "availability_topic": config[device].get('availability_topic')
            }
        messages.append({'topic': 'homeassistant/sensor/'+config[device].get('topic')+'_temperature/config', \
                         'payload': json.dumps(payload), 'retain': config[device].getboolean("retain", False)})
        #humidity
        payload["name"] = device + " Humidity"
        payload['unit_of_measurement'] = "%"
        payload["device_class"] = "humidity"
        payload["value_template"] = '{{ value_json.humidity }}'
        messages.append({'topic': 'homeassistant/sensor/'+config[device].get('topic')+'_humidity/config', \
                         'payload': json.dumps(payload), 'retain': config[device].getboolean("retain", False)})
        #battery
        payload["name"] = device + " Battery"
        payload['unit_of_measurement'] = "%"
        payload["device_class"] = "battery"
        payload["value_template"] = '{{ value_json.battery }}'
        messages.append({'topic': 'homeassistant/sensor/'+config[device].get('topic')+'_battery/config', \
                         'payload': json.dumps(payload), 'retain': config[device].getboolean("retain", False)})
    return messages

def delete_ha_config(config:configparser.ConfigParser,devices):
    messages = []
    for device in devices:
        messages.append({'topic': 'homeassistant/sensor/'+config[device].get('topic')+'_temperature/config', \
                         'payload': "", 'retain': True})
        messages.append({'topic': 'homeassistant/sensor/'+config[device].get('topic')+'_humidity/config', \
                    'payload': "", 'retain': True})
        messages.append({'topic': 'homeassistant/sensor/'+config[device].get('topic')+'_battery/config', \
                    'payload': "", 'retain': True})

    return messages