import paho.mqtt.client as mqtt
import mysql.connector
import json
import pandas as pd
import csv
from datetime import datetime
import pymongo

mqtt_Topic="Esp32data"
mongo_database="mydb"
mongo_collection="esp"

mysql_host="localhost"
mysql_user="root"
mysql_password="password"
mysql_database="espdatabase"
mysql_table="espdata"

logfile="D:\\python code\\Esp32IOTlog.txt"
csvFilename="D:\\python code\\Esp32csvlog.csv"
def logtime():
    currenttime=datetime.now()
    ctime=currenttime.strftime("%Y/%m/%d %H:%M:%S")
    return ctime
# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to broker")
        # Subscribe to a topic after successful connection
        client.subscribe(mqtt_Topic,qos=2)  
        entry=f"{logtime()} -MQTT-Connection-possitive\n"
        with open(logfile,"a") as log_file:
            log_file.write(entry)
            log_file.close()
            print("MQTT-connection-possitive-logged")
             
    else:
        entry=f"{logtime()} - MQTT-connection-failed Rc={rc}\n"
        with open(logfile,"a") as log_file:
            log_file.write(entry)
            log_file.close()
            print(f"MQTT-connection-failed-rc:{rc}-logged")
# Callback when a message is received from the broker
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
    entry=f"{logtime()} -MQTTData-received-possitive\n"
    with open(logfile,"a") as log_file:
        log_file.write(entry)
        log_file.close()
        print(f"MQTTData-received-possitive-logged")
    now=datetime.now()
    ftime=now.strftime("%Y/%m/%d %H:%M:%S")
    data=json.loads(msg.payload.decode())
    jsondata=dict(UpdatedTime=ftime)
    jsondata.update(data)
    print(f"json data is : {jsondata} and its type was {type(jsondata)}")
    df=pd.DataFrame([jsondata])
    df.to_csv(csvFilename,mode='a',header=False,index=False)
    entry=f"{logtime()} -CSVFile-Data storing-possitive\n"
    with open(logfile,"a") as log_file:
        log_file.write(entry)
        log_file.close()
        print(f"CSVData-storing-possitive-logged")
    storemongo(jsondata)
    storemysql(jsondata)

#Store data in mongodb
def storemongo(data):
    try:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        print(f"MongoDb connection status: {myclient.admin.command('ping')}")
        print(f"Mongodb connection successfully")
        mydb = myclient[mongo_database]
        mycol = mydb[mongo_collection]
        x = mycol.insert_one(data)
        if (x.inserted_id):
            entry=f"{logtime()} -Mongodb-Data storing-possitive\n"
            with open(logfile,"a") as log_file:
                log_file.write(entry)
                log_file.close()
                print(f"Mongodb-Data storing-possitive-logged")
        else:
            entry=f"{logtime()} - Mongodb-Data storing-negative\n"
            with open(logfile,"a") as log_file:
                log_file.write(entry)
                log_file.close()
                print(f"Mongodb-Data storing-negative-logged")
    except:
        print(f"Mongodb connection failed")
        entry=f"{logtime()} -Mongodb-Connection-negative\n"
        with open(logfile,"a") as log_file:
            log_file.write(entry)
            log_file.close()
            print(f"Mongodb-connection-negative-logged")


#Store data in mysql
def storemysql(data):
    try:
       mydb=mysql.connector.connect(host=mysql_host,user=mysql_user,password=mysql_password,database=mysql_database)
       print(f"my sql status :{mydb.is_connected()}")
       if (mydb.is_connected):
           print("My sql connected successfully")
           entry=f"{logtime()} -Mysql-connection-possitive\n"
           with open(logfile,"a") as log_file:
                  log_file.write(entry)
                  log_file.close()
                  print(f" mysql-connection-possitive-logged")
       else:
           pass
       mycursor=mydb.cursor()
       col="INSERT INTO mysql_table (`Updated_Time`, `Gateway_Time`, `Count`, `MAC`, `IP`, `RSSI`) VALUES(%s,%s,%s,%s,%s,%s)"
       val=(data["UpdatedTime"],data["Gateway time"],data["Count"],data["MAC ID"],data["IP"],data["RSSI"])
       mycursor.execute(col, val)
       mydb.commit()
       print(mycursor.rowcount, "record inserted.")
       if (mycursor.rowcount==1):
              entry=f"{logtime()} - Mysql-data storing-possitive\n"
              with open(logfile,"a") as log_file:
                  log_file.write(entry)
                  log_file.close()
                  print(f"Mysql-data storing-possitive-logged")
       else:
              entry=f"{logtime()} - Mysql-data storing-negative\n"
              with open(logfile,"a") as log_file:
                  log_file.write(entry)
                  log_file.close()
                  print(f" Mysql-data storing-negative")
       #sendmysql(data)
       
    
    
        
    except:
        print("mysql connection faild")
        entry=f"{logtime()} - Mysql-connection-negative\n"
        with open(logfile,"a") as log_file:
            log_file.write(entry)
            log_file.close()
            print(f"Mysql-connection-negative-logged")
# Create an MQTT client instance
client = mqtt.Client()

# Assign event callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker (replace with your broker details)
broker_address = "broker.emqx.io"  # Public test broker, replace with your broker address
port = 1883  # Default MQTT port

# Connect to the broker
client.connect(broker_address, port)
# Blocking call that processes network traffic, dispatches callbacks, and handles reconnecting.
client.loop_forever()