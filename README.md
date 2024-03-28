
# About
This is simple python script, which scans Xiaomi BLE Temperature and Humidity sensors and publishes measurements to MQTT. 

It supports LYWSD03MMC and LYWSDCGQ(MJ_HT_V1) sensors, can be easily extended to LYWSD03.

# Installation

1.Install required packages:
    
    sudo pip3 install bluepy
    sudo pip3 install paho-mqtt
    sudo pip3 install lywsd03mmc
    
1.1.If you're using Ubuntu 20.04 on Raspberry Pi:

    sudo apt-get install libglib2.0-dev pi-bluetooth 
    sudo pip3 install btlewrap

2.Clone code:

    git clone https://github.com/algirdasc/xiaomi-ble-mqtt.git
    cd xiaomi-ble-mqtt

3.Add crontab task. Task will be run every 5 minutes:

    crontab -e
	# Add row
	*/5 * * * * /usr/bin/python3 <path to xiaomi-ble-mqtt>/data-read.py >> <path to xiaomi-ble-mqtt>/xiaomi-ble.log 2>&1

4.Rename `mqtt.ini.sample` to `mqtt.ini` and configure MQTT broker by editing `mqtt.ini` file.

5.Scan for available Xiaomi BLE devices:

     sudo hcitool lescan

Look for line which looks like this: 

    4C:65:A8:D4:A3:1D MJ_HT_V1

5.Rename `devices.ini.sample` to `devices.ini` and configure Xiaomi devices by editing `devices.ini` file:

    [room1]
    device_mac=4C:65:A8:XX:XX:XX
    topic=sensors/room1
    availability_topic=sensors/room1/availability
    average=3
    retain=1
    timeout=10
    
    [room2]
    device_mac=4C:65:A8:XX:XX:XX
    topic=sensors/room2
    
    etc...

MQTT Payload example:

    {"temperature": 25.7, "humidity": 42.0, "battery": 100}

