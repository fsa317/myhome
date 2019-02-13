from __future__ import division
from flask import Flask, request, send_from_directory
from pymongo import MongoClient
import configparser
import sys
import math
import paho.mqtt.client as mqtt
import requests
import time
import json
import datetime
import random

#https://www.tutorialspoint.com/python/python_reading_rss_feed.htm
#https://pypi.org/project/sports.py/

#http://mlb.mlb.com/partnerxml/gen/news/rss/nym.xml


app = Flask(__name__,static_url_path='')
app.debug = False
DEBUG = True
config = configparser.ConfigParser()
config.read('ticker.ini')
currentSource = None

tickerip = "192.168.1.13"

@app.route("/ticker/getnextsource")
def doGetNextSource():
    processTickerEvent("fromticker/getnextsource","msg")
    return "OK"

@app.route("/ticker/setmsg/<idx>/<msg>")
def setTickerMsg(idx,msg):
    config['custom']['m'+str(idx)]=msg
    saveConfig()
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

def sendTickerMsg(idx,msg):
    dprint("Publishing ticker msg "+str(idx)+": "+msg)
    mqttc.publish("toticker/setmsg",str(idx)+msg)

def clearTickerMessages():
    mqttc.publish("toticker/clearmsgs","clearall")

def sendMessagesFromSource():
    msgs = None
    print("currentSource " + currentSource)
    if (currentSource == "custom"):
        dprint("Handling Custom messages")
        msgs = getCustomMessages()
    else:
        print("Unknown source")
    if (msgs is not None):
        sendAllMsgs(msgs)

def sendAllMsgs(msgs):
    idx = 0
    clearTickerMessages()
    for m in msgs:
        sendTickerMsg(idx,m)
        idx = idx +1

def getCustomMessages():
    customMsgs = config['custom']
    msgs = []
    for key in customMsgs:
        msgs.append(customMsgs[key])
    return msgs

def processTickerEvent(topic,msg):
    global currentSource
    dprint("Ticker Event "+topic+" "+msg)
    if (topic == "fromticker/getnextsource"):
        currentSource = getNextSource()
        print("getting source: "+currentSource)
        sendMessagesFromSource()

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
    if (msg.topic.startswith("fromticker")):
        processTickerEvent(msg.topic, msg.payload)
    if (msg.topic.startswith("regserver")):
        processRegServer(msg.topic,msg.payload)

#CONFIG
def saveConfig():
    with open('ticker.ini', 'w') as configfile:
        config.write(configfile)

def getNextSource():
    sources = config['sources']
    foundCurrent = False
    for key in sources:
        if (foundCurrent and sources[key] == "yes"):
            return key
        if (key == currentSource):
            foundCurrent = True
    #if we got here we can just return the first on source
    for key in sources:
        if (sources[key] == "yes"):
            return key

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

if __name__ == "__main__":
    print(config.sections())
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
