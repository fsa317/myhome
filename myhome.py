from __future__ import division
from flask import Flask, request, send_from_directory
from pymongo import MongoClient

import sys
import math
import paho.mqtt.client as mqtt
import requests
import time
import json
import gmail
import datetime

# http://forum.micasaverde.com/index.php/topic,35848.75.html  VERA MQTT Plugin

#5166437472@tmomail.net
#http://stackoverflow.com/questions/10147455/how-to-send-an-email-with-gmail-as-provider-using-python

app = Flask(__name__,static_url_path='')
app.debug = False
mClient = MongoClient()
mDB = mClient.wine


lastunlocktime = 0
lastmotion = 0
fireplaceip = "192.168.1.8"
wineip = "192.168.1.99"
tickerip = "192.168.1.13"
winedata = {}       #latest values of all things sent
winedata_ts = {}    #timestamps for all values sent
MAX_LIST_COUNT = 1000
wine_roomtemp_list = []
fireplaceState = 0


DEBUG = True

def dprint(str):
    if (DEBUG == True):
        print(str)
    sys.stdout.flush()

def getAverage(lst):
    return sum(lst) / len(lst)

def getVariance(lst):
    average = getAverage(lst)
    variance = sum((average - value) ** 2.0 for value in lst) / len(lst)
    return variance

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

#DEF ACTIONS


def turnOnFireplace():
    print("Turn on fireplace");
    url = "http://"+fireplaceip+"/fireplaceon"
    print("Requesting "+url)
    r = requests.get(url)
    print ("Response "+r.text)
    sys.stdout.flush()
    global fireplaceState
    fireplaceState = 1
    mqttc.publish("oh/fireplace",fireplaceState)
    mqttc.publish("ha/fireplace",fireplaceState)
    return r.text

def turnOffFireplace():
    print("Turn off fireplace");
    url = "http://"+fireplaceip+"/fireplaceoff"
    print("Requesting "+url)
    r = requests.get(url)
    print ("Response "+r.text)
    sys.stdout.flush()
    global fireplaceState
    fireplaceState = 0
    mqttc.publish("oh/fireplace",fireplaceState)
    mqttc.publish("ha/fireplace",fireplaceState)
    return r.text


def processRegServer(topic,msg):
    global fireplaceip
    tmp = msg.split(':')
    name = tmp[0];
    addr = tmp[1];
    dprint("Server Reg "+name+" "+addr)
    if (name == "Fireplace"):
        dprint("Fireplace IP set to "+addr)
        fireplaceip = addr
        saveSystemIP("Fireplace",addr)
    if (name == "Wine"):
        dprint("Wine IP set to "+addr)
        wineip = addr
        saveSystemIP("Wine",addr)
    if (name == "Ticker"):
        dprint("Ticker set to "+addr)
        tickerip = addr
        saveSystemIP("Ticker",addr)
    sys.stdout.flush()

def processWineData(topic,msg):
    global winedata
    tmp = msg.split("=")
    name = tmp[0];
    val = tmp[1];
    winedata[name] = val
    winedata_ts[name] = datetime.datetime.now()
    mqttc.publish("oh/wine/"+name,val)
    mqttc.publish("ha/wine/"+name,val)
    if (name == "Room Temp"):
        insertRoomTemp(val)
        #dprint(wine_roomtemp_list)

def processFireplace(topic,msg):
    if (msg=="1"):
        turnOnFireplace()
    if (msg=="0"):
        turnOffFireplace()


#MQTT processing
def on_connect(client, obj, rc):
    print("mqtt connect rc: " + str(rc))
    client.subscribe("wine/#")
    client.subscribe("Vera/#")
    client.subscribe("regserver")
    client.subscribe("myhome/#")
    sys.stdout.flush()

def on_message(client,userdata,msg):
    print(msg.topic+" "+str(msg.payload))
    if (msg.topic.startswith("Vera")):
        processVeraEvent(msg.topic, msg.payload)
    if (msg.topic.startswith("regserver")):
        processRegServer(msg.topic,msg.payload)
    if (msg.topic.startswith("wine/data")):
        processWineData(msg.topic,msg.payload)
    if (msg.topic.startswith("myhome/fireplace")):
        processFireplace(msg.topic,msg.payload)
    if (msg.topic.startswith("myhome/wine/setdesiredtemp")):
        dprint("DBG: "+msg.payload)
        mqttc.publish("winebot/settemp",msg.payload)
    if (msg.topic.startswith("myhome/wine/setfinmintemp")):
        dprint("DBG2: "+msg.payload)
        mqttc.publish("winebot/setfinmintemp",msg.payload)
    if (msg.topic.startswith("myhome/wine/setheaterpower")):
        dprint("DBG3: "+msg.payload)
        mqttc.publish("winebot/setheaterpower",msg.payload)
    sys.stdout.flush()

def insertRoomTemp(val):
    tmp = datetime.datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0)
    mDB.roomtemps.update_one(
      {'date': tmp},
      {
        '$push': { 'temps': {'val':float(val), 'dt': datetime.datetime.utcnow() } }
      },
      upsert=True
    )

#REST handling
@app.route("/wine/settemp/<val>")
def setTemp(val):
    mqttc.publish("winebot/settemp",val)
    return "OK"

@app.route("/wine/setfinmintemp/<val>")
def setFinMinTemp(val):
    mqttc.publish("winebot/setfinmintemp",val)
    return "OK"

@app.route("/wine/setheaterpower/<val>")
def setHeaterPower(val):
    mqttc.publish("winebot/setheaterpower",val)
    return "OK"

@app.route("/wine/gettemp")
def getTemp():
    s = winedata["Room Temp"]
    dt = str(winedata_ts["Room Temp"])
    return s+":"+dt

@app.route("/wine/getfintemp")
def getFinTemp():
    s = winedata["Fin Temp"]
    dt = str(winedata_ts["Fin Temp"])
    return s+":"+dt

@app.route("/wine/getcooling")
def getCooling():
    s = winedata["Cooling"]
    dt = str(winedata_ts["Cooling"])
    return s+":"+dt

@app.route("/wine/getdefrosting")
def getDefrosting():
    s = winedata["Defrosting"]
    dt = str(winedata_ts["Defrosting"])
    return s+":"+dt

@app.route("/wine/gethumidity")
def getHumidity():
    s = winedata["Humidity"]
    dt = str(winedata_ts["Humidity"])
    return s+":"+dt

@app.route("/wine/roomstats")
def getRoomStats():
    aTemp = getAverage(wine_roomtemp_list)
    aVar = getVariance(wine_roomtemp_list)
    return "Temp: "+aTemp+", Variance: "+variance

@app.route("/fireplace/on")
def fireplaceOn():
    return turnOnFireplace()

@app.route("/fireplace/off")
def fireplaceOff():
    return turnOffFireplace()


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

@app.route("/")
def getHome():
    return send_from_directory('html', 'home.html')

def sendTickerMsg(msg):
    print "Publishing ticker msg "+msg
    mqttc.publish("ticker/addmsg","          "+msg+"          ")

def clearTickerMessages():
    mqttc.publish("ticker/clearmsg","clearall")

### MAIN
if __name__ == "__main__":
    print "Connecting to mqtt"
    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect("127.0.0.1")
    fireplaceip = getSystemIP("Fireplace")
    wineip = getSystemIP("Wine")
    print "Defaulted fireplaceip "+fireplaceip
    print "Default wineip "+wineip
    sys.stdout.flush()
    mqttc.loop_start()
    app.run(host='0.0.0.0', port=80, debug=True,use_reloader=False)
    print "Doing other stuff"
