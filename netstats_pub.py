"""
netstats_pub.py is an example of a publisher of network stats of various Rasberry Pi nodes at UPC

"""


import paho.mqtt.client as mqtt
import time
import re
import json
import argparse
import csv
import sys
import os
import re
from influxdb import InfluxDBClient
import base64



global IFclient,objects
json_body=[]
contents={}
contents["measurement"]= "Network"
contents["tags"]={}
contents["tags"]["mac"]=' '
contents["tags"]["ESSID"]=" "
contents["tags"]["PI_ID"]=9012
contents["fields"]={}





####################Connect to InfluxDB##############################################33
####InfluxDB configuration#######
IFclient = InfluxDBClient('eclipse.usc.edu', 10002, 'loracciuser','lora4cci', 'loracci')





def on_connect(client, userdata, flags, rc):
    """print out result code when connecting with the broker
    Args:
        client: publisher
        userdata:
        flags:
        rc: result code
    Returns:
    """

    m="Connected flags"+str(flags)+"result code "\
    +str(rc)+"client1_id  "+str(client)
    print(m)


def percentage(part, whole):
  return 100 * float(part)/float(whole)

#define function



def on_message(client1, userdata, message):
    """print out recieved message
    Args:
        client1: publisher
        userdata:
        message: recieved data
    Returns:
    """
    print("message received  "  ,str(message.payload.decode("utf-8")))


if __name__ == '__main__':



    account = "gowri"
    pw = "7rU7386G"
    topic = "USC/UPC/NetworkStats"


    #connect to broker
    try:
        pub_client = mqtt.Client(account)
        pub_client.on_connect = on_connect
        pub_client.on_message = on_message
        pub_client.username_pw_set(account, pw)
        pub_client.connect('dsicloud3.usc.edu', 1880)

    except Exception as e:
        print "Exception" + str(e)

    #get json data from api endpoint


while 1:
    os.system('iwlist wlan0 scan |bash sni.sh >b.txt')
    lines = open("b.txt", "r").readlines()[1:]
    my_dictionary={}

    for line in lines:
        match =re.search(r'mac',line)
        if match is None:
            part=re.split(r' +"',line)
            my_dictionary[str(part[0])]=str(part[1])
    for key in my_dictionary:
        lin=my_dictionary[key]
        p = re.split(r'"+', lin)
        contents["fields"]["ESSID"] = p[0]
        contents["tags"]["ESSID"]=p[0]
        split_again = re.split(r' +', p[1])
        contents["fields"]["Channel_Frequency"] = split_again[1]
        partition = re.split(r'/', split_again[3])
        part = partition[0]
        whole = partition[1]
        contents["fields"]["Channel_Quality"] = percentage(part, whole)
        contents["fields"]["Noise_Level"] = split_again[4]

        json_body.append(contents)
        print("Write points: {0}".format(json_body))
        if contents["fields"]:
            IFclient.write_points(json_body)

    #publish
    pub_client.publish(topic, json.dumps(my_dictionary))
    time.sleep(100)




pub_client.disconnect()
