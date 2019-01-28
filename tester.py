from __future__ import division
from flask import Flask

import sys
import math
import paho.mqtt.client as mqtt
import requests
import time
import json
import gmail



def dprint(str):
    if (DEBUG == True):
        print(str)

def nowMS():
    return int(round(time.time() * 1000))

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))
    print("mosq: "+str(mosq))
    print("obj: "+str(obj))


#MQTT processing
def on_connect(client, obj, rc):
    print("mqtt connect rc: " + str(rc))
    client.subscribe("hass/#")

def on_message(client,userdata,msg):
	print(msg.topic+" -- "+str(msg.payload))
#MAIN

print "Connecting to mqtt"
mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_message = on_message
mqttc.connect("127.0.0.1")
sys.stdout.flush()

print "Starting test"
#mqttc.publish("oh/wine/DesiredTemp","61")
#mqttc.publish("oh/wine/finMinTemp","61")
#mqttc.publish("oh/wine/deadband","3")
#mqttc.publish("oh/wine/heaterPower","500")

#mqttc.publish("oh/wine/Fin Temp","39")
#mqttc.publish("oh/wine/Room Temp","49")
#mqttc.publish("oh/wine/Cooling","1")
#mqttc.publish("oh/wine/Defrosting","0")
#mqttc.publish("oh/wine/Humidity","41")




while True:
	mqttc.loop()
