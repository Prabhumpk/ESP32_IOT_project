import pymongo
from datetime import datetime,timedelta 
import time
import schedule
import mysql.connector
import json
import pandas as pd
import csv

mongo_database="mydb"
mongo_collection="esp"

mysql_host="localhost"
mysql_user="root"
mysql_password="password"
mysql_database="espdatabase"
mysql_table="esp_scheduler"

num=1
nums=0
logfile="D:\\python code\\Esp32schedulerlog.txt"
def logtime():
    currenttime=datetime.now()
    ctime=currenttime.strftime("%d/%m/%Y %H:%M:%S")
    return ctime
def getdata(count,datacount):
    try:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        print(f"MongoDb connection status: {myclient.admin.command('ping')}")
        print(f"Mongodb connection successfully")
        entry=f"{logtime()} -Mongodb-Connection-possitive\n"
        with open(logfile,"a") as log_file:
            log_file.write(entry)
            log_file.close()
            print(f"Mongodb-Connection-possitive-logged")
        mydb = myclient[mongo_database]
        mycol = mydb[mongo_collection]
        end_time = datetime.now()
        to_time=end_time.strftime("%Y/%m/%d %H:%M:%S")
# Subtract one hour
        start_time = end_time - timedelta(minutes=1)
        from_time=start_time.strftime("%Y/%m/%d %H:%M:%S")
        print(f"Loop count is {count} and time {datetime.now()}")
        print(f"Start time is {start_time.strftime("%Y/%m/%d %H:%M:%S")}")
        print(f"End time is : {end_time.strftime("%Y/%m/%d %H:%M:%S")}")
    except:
        print(f"Mongodb connection failed")
        entry=f"{logtime()} -Mongodb-Connection-negative\n"
        with open(logfile,"a") as log_file:
            log_file.write(entry)
            log_file.close()
            print(f"Mongodb-connection-negative-logged")
    try:
        for doc in mycol.find({"Gateway time":{"$gte":from_time,"$lte":to_time}}):
            sqldb=mysql.connector.connect(host=mysql_host,user=mysql_user,password=mysql_password,database=mysql_database)
            print(f"my sql status :{sqldb.is_connected()}")
            if (sqldb.is_connected):
                print("My sql connected successfully")
                entry=f"{logtime()} -Mysql-connection-possitive\n"
                with open(logfile,"a") as log_file:
                    log_file.write(entry)
                    log_file.close()
                    print(f" mysql-connection-possitive-logged")
            else:
                pass
            mycursor=sqldb.cursor()
            col="INSERT INTO mysql_table (`Updated time`, `gateway time`, `Count`, `MAC ID`, `IP`, `RSSI`) VALUES(%s,%s,%s,%s,%s,%s)"
            val=(doc["UpdatedTime"],doc["Gateway time"],doc["Count"],doc["MAC ID"],doc["IP"],doc["RSSI"])
            mycursor.execute(col, val)
            sqldb.commit()
            print(mycursor.rowcount, "record inserted.")
            if (mycursor.rowcount==1):
                entry=f"{logtime()} - Mysql-data {datacount} storing-possitive\n"
                with open(logfile,"a") as log_file:
                    log_file.write(entry)
                    log_file.close()
                    print(f"Mysql-data {datacount} storing-possitive-logged")
            else:
                entry=f"{logtime()} - Mysql-data {datacount} storing-negative\n"
                with open(logfile,"a") as log_file:
                    log_file.write(entry)
                    log_file.close()
                    print(f" Mysql-data {datacount} storing-negative")
            datacount+=1
            print(doc)
    except:
        entry=f"{logtime()} - Mysql-Connection-Negative\n"
        with open(logfile,"a") as log_file:
            log_file.write(entry)
            log_file.close()
            print(f"Mysql-Connection-Negative-logged") 
            
       #sendmysql(data)
    
    count+=1
    print(f"Total data count is : {datacount}")    
schedule.every(1).minutes.at(":00").do(getdata,count=num,datacount=nums)
while True:
    try:
        schedule.run_pending()
    except:
        entry=f"{logtime()} -Error occured while schedule a job \n"
        with open(logfile,"a") as log_file:
            log_file.write(entry)
            log_file.close()
            print(f"Error occured while schedule a job")
    time.sleep(0.1)
  