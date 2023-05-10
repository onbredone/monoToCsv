#!/usr/bin/python
import calendar
from email import encoders
from email.mime.base import MIMEBase
import json
import requests
import datetime
import time
import csv
import smtplib, ssl
import codecs
import sys
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.application import MIMEApplication

#TODO
#Fix wrong filename send in mail
#Fix file encoding. Should be windows-1250 and no issues with krakozyabra

def insert_dot(string):
    return string[:len(string)-2] + '.' + string[len(string)-2:]

#monobank API data
x_token = "{your Monobank token here}"
base_url= "{pi baseurl}"

#Acemoney csv data format
row_list = [["№","Дата","Кореспондент","Категорiя","С","Видатки","Дохід","Разом","Коментар"]]

#Month to get data
year = '2023'
month = '4'

filename = f'MonoReport_{year}_{month}.csv'
#get days amount in month
days_in_month = calendar.monthrange(int(year), int(month))[1]

#get timestamp of start date
start = time.mktime(datetime.datetime.strptime(f'{year}-{month}-1', "%Y-%m-%d").timetuple())

#get timestamp of start date
end = start + (days_in_month * 24 * 3600)

#convert dates timestamps to strings
startDate = str(start).rstrip('0').rstrip('.')
endDate = str(end).rstrip('0').rstrip('.')
print("Strat timestamp: " + startDate)
print("End timestamp: " + endDate)

#get data from monobank API
HEADERS = {'x-token': x_token}

r = requests.get(url = base_url + startDate + "/" + endDate, headers = HEADERS)

data = json.loads(r.content)

#parse data to rows
for i in data:
    if "comment" in i:
        comment = " - " + i["comment"]
    else:
        comment = ""
    row = ["",datetime.datetime.fromtimestamp(i['time']).strftime("%d/%m/%Y"),"","","","",insert_dot(str(i['amount'])),"", i['description'] + comment]
    print(row)
    row_list.append(row)
#print(data)

#save data to file
with open(filename, 'w', newline='', encoding="utf-8") as file:
    writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC,
                        delimiter=',', quotechar='"')
    writer.writerows(row_list)

#convert encoding
def convert_encoding():
    sourceEncoding = "utf-8"
    targetEncoding = "windows-1250"
    source = open(filename)
    target = open(filename+"converted", "w")
    read_encoded = source.read().decode(sourceEncoding)
    target.write(read_encoded.encode('windows-1250'))

#build mail
def build_mail():
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    #Replace with your own gmail account
    gmail = '{your gmail to get the file}'
    password = '{mail pasword}'

    message = MIMEMultipart()
    message['From'] = 'Contact <{sender}>'.format(sender = gmail)
    message['To'] = gmail
    message['Subject'] = 'Your financial report from Monobank'    
    mail_content = '''Hi,
    please find file attached'''

    attach_file_name = f"quotes{month}.csv"
    message.attach(MIMEText(mail_content, 'plain'))
    attach_file = open(attach_file_name, 'rb') # Open the file as binary mode
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload((attach_file).read())
    encoders.encode_base64(payload) #encode the attachment
    #add payload header with filename
    payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
    message.attach(payload)
    context = ssl.create_default_context()
    text = message.as_string()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()  
        server.starttls(context=context)
        server.ehlo()
        server.login(gmail, password)
        server.sendmail(gmail, gmail, text)
        server.quit()
    print("email sent out successfully")

#build_mail()
