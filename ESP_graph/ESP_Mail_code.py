#The Code fetch data from mysql and plot graph and send that graph as a pdf to mail
import mysql.connector
import json
import pandas as pd
import csv
from datetime import datetime,timedelta 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import time
import schedule
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

sender_email = "prabhakaranmanickam2002@gmail.com"
app_password = "upez tkno gpmn brcw"  # Use App Password if Gmail, regular password otherwise
receiver_email = "prabhakaranm2802@gmail.com"

# Create the email subject, sender, receiver


#list=[]
#x=[]
#y=[]
#count=0
myindex=["Updated time","Gateway time","Count","MAC ID","IP","RSSI"]
def getsqldata(f_time,t_time,count=0,x=[],y=[],list=[]):
  sqldb=mysql.connector.connect(host="localhost",user="root",password="",database="test")
  mycursor=sqldb.cursor()
  col="""SELECT * FROM `esp` WHERE `Gateway time` BETWEEN %s AND %s"""
  val=[f_time,t_time]
  mycursor.execute(col,val)
  results = mycursor.fetchall()  
  mycursor.close()
  sqldb.close()
  return results

def plotdata(s_time,e_time):
  from_time=datetime.strptime(s_time,f"%Y/%m/%d %H:%M:{"00"}")#convert str formatted datetime into datetime object
  to_time=datetime.strptime(e_time,f"%Y/%m/%d %H:%M:{"00"}")
  #print(f"S time dtype plotdata func is : {from_time}")
  #print(f"E time dtype plotdata func is : {to_time}")
  start_time = to_time - timedelta(minutes=5)
  filetime=datetime.strftime(to_time,f"%Y-%m-%d %H_%M_{"00"}")
  #print(f"S time strtype plotdata func is : {s_time}")
  #print(f"E time strtype plotdata func is : {e_time}")
  data=getsqldata(f_time=s_time,t_time=e_time)
  if data:
     filename=f"RSSI_Graph_{filetime}.pdf"
     print(f"File name is : {filename}")
     Gatewaytime,Updatedtime,Count,MAC_ID,IP,RSSI=zip(*data)
     x_val=[]
     a_val=[]
     for row in Gatewaytime:
        a=row[-8:]
        d_val=datetime.strptime(row,"%Y/%m/%d %H:%M:%S")
        x_val.append(d_val)
     x_ticks = [from_time+timedelta(seconds=60*i) for i in range(0,6)]  # for row i
     fig,ax=plt.subplots(figsize=(10,4))
     ax.plot(x_val, RSSI,color='blue', label="RSSI Value Over Time")
     ax.xaxis.set_major_locator(mdates.SecondLocator(interval=60))
     ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
     ax.set_xlabel("Time")
     ax.set_ylabel("RSSI")
     ax.set_title(f"RSSI Data From {from_time} to {to_time}")
     ax.grid(True)
     ax.legend()
     plt.tight_layout()
     plt.savefig(filename)
     return filename
  else:
     print("NO data from sql")
def sendmail():
   end_time_dt=datetime.now() #dt refers Dtype
   start_time_dt = end_time_dt - timedelta(minutes=5)
   #print(f"Start time Dtype sendmail func is : {start_time_dt}")
   #print(f"End time Dtype sendmail func is : {end_time_dt}")

   from_time=start_time_dt.strftime(f"%Y/%m/%d %H:%M:{"00"}")
   to_time=end_time_dt.strftime(f"%Y/%m/%d %H:%M:{"00"}")
   #print(f"From time strtype sendmail func is : {from_time}")
   #print(f"To time strtype sendmail func is : {to_time}")
   fname=plotdata(s_time=from_time,e_time=to_time)# Pass str time formet to plot data function
   message = MIMEMultipart()
   message['From'] = sender_email
   message['To'] = receiver_email
   message['Subject'] = f"RSSi Graph B/W {from_time} and {to_time}"

   # Email body content
   body = "Hello, appa."
   message.attach(MIMEText(body, 'plain'))
   with open(fname, "rb") as attachment:
    # Create a MIMEBase object and add the PDF content to it
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename= {fname}')
    message.attach(part)
    try:
       # Connect to Gmail's SMTP server (or another provider)
       server = smtplib.SMTP('smtp.gmail.com', 587)
       server.starttls()  # Secure the connection

       # Login to your email account
       server.login(sender_email, app_password)

       # Send the email with the attachment
       text = message.as_string()
       server.sendmail(sender_email, receiver_email, text)
       print("Email sent successfully with PDF attachment!")

    except Exception as e:
       print(f"Error: {e}")

    finally:
       server.quit()  # Close the connection to the server
     
#sendmail() 
  #plt.show()
#getsqldata(count)

schedule.every(5).minutes.at(":05").do(sendmail)# Run every 5 minutes

while True:
    try:
       schedule.run_pending()
    except Exception as e:
       print(f"An Error occured while scheduler running : {e}")
    finally:
       time.sleep(0.1)
