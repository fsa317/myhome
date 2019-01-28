from __future__ import division
from flask import Flask, request, send_from_directory
from pymongo import MongoClient

import sys
import math
import paho.mqtt.client as mqtt
import requests
import time
import json
import datetime
import random

app = Flask(__name__,static_url_path='')
app.debug = False
DEBUG = True

tickerip = "192.168.1.13"

@app.route("/ticker/addmsg/<msg>")
def setTickerMsg(msg):
    print "Set Ticker Msg - "+msg
    sendTickerMsg(msg)
    return "OK"

@app.route("/ticker/clearmsgs")
def clearTickerMsg(msg):
    print "Clear Ticker Msgs - "
    clearTickerMessages()
    return "OK"

@app.route("/ticker/btn/<btnname>")
def doButton(btnname):
    print("doButton "+btnname)
    mqttc.publish("toticker/btn",btnname)
    return "OK"

@app.route("/")
def getHome():
    return send_from_directory('html', 'ticker.html')

def sendTickerMsg(msg):
    print "Publishing ticker msg "+msg
    mqttc.publish("toticker/addmsg","          "+msg+"          ")

def clearTickerMessages():
    mqttc.publish("toticker/clearmsg","clearall")

def dprint(str):
    if (DEBUG == True):
        print(str)
    sys.stdout.flush()

def nowMS():
    return int(round(time.time() * 1000))

def saveSystemIP(sysname,ipaddr):
    f = open(sysname+".ip","w")
    f.write(ipaddr)
    f.close()

def getSystemIP(sysname):
    f = open(sysname+".ip","r")
    r = f.read()
    f.close
    return r

def processTickerEvent(topic,msg):
    dprint("Ticker Event "+topic+" "+msg)

def processRegServer(topic,msg):
    tmp = msg.split(':')
    name = tmp[0];
    addr = tmp[1];
    if (name == "Ticker"):          # MY HOME handles writing to file this is just for runtime changes
        dprint("Ticker.ip set to "+addr)
        tickerip = addr

#MQTT processing
def on_connect(client, obj, rc):
    print("mqtt connect rc: " + str(rc))
    client.subscribe("fromticker/#")
    client.subscribe("regserver")
    sys.stdout.flush()

def on_message(client,userdata,msg):
    print("RCVD: "+msg.topic+" "+str(msg.payload))
    if (msg.topic.startswith("ticker")):
        processTickerEvent(msg.topic, msg.payload)
    if (msg.topic.startswith("regserver")):
        processRegServer(msg.topic,msg.payload)

if __name__ == "__main__":
    print "Connecting to mqtt"
    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect("127.0.0.1")
    tickerip = getSystemIP("Ticker")
    dprint("TICKER IP "+tickerip)
    sys.stdout.flush()
    mqttc.loop_start()
    app.run(host='0.0.0.0', port=81, debug=True,use_reloader=False)
    print "Doing other stuff"
