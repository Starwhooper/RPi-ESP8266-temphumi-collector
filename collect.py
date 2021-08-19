#!/usr/bin/python3
# Creator: Thiemo Schuff, thiemo@schuff.eu
# Source: https://github.com/Starwhooper/RPi-ESP8266-temphumi-collector
# <!--get awesomefonts from here: https://fontawesome.com/v5.15/icons/cloud-sun?style=solid //-->

try: from getmac import get_mac_address
except:
	print('python3 modul getmac is missed')
	print('please do follow command to get it:')
	print('sudo apt-get install python3-pip && sudo pip3 install getmac')
	exit()

import urllib.request
import socket
import datetime
import time
import os
import sys
import json

ip = str((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])
ipareaparts = ip.split('.')

##########check environment
try: htmlfile = open('/var/www/html/weather.html','w')
except:
	print('file /var/www/html/weather.html not aviable of permission missed')
	print('please do follow command to get it:')
	print('sudo touch /var/www/html/weather.html && sudo chmod 777 /var/www/html/weather.html')

##########Functions
def calc_abs_humi(relhumi,temp):
 return(round(10 ** 5 * 18.016 / 8314.3 * float(relhumi) / 100 * 6.1078 * 10**( ( 7.5 * float(temp) ) / ( 237.3 + float(temp) ) ) / ( float(temp) + 273.15 )))

def return_date():
 return(datetime.date.today().strftime('%d. %b. \'%y'))

def return_time():
 return(time.strftime('%H:%M', time.localtime()))

def return_todo(relhumi,abshumi,absoutdoorhumi):
 todo = ''
 if float(relhumi) < 40:
  todo += 'An diesem Ort ist die Luftfeuchtigkeit zu niedrig'
  if absoutdoorhumi < abshumi: todo += ', da die abs. Feuchte drau&szlig;sen niedriger ist, sollte nicht gel&uuml;ftet werden um die Luftfeuchtigkeit m&ouml;glichst zu erhalten. <i class="fas fa-door-closed"></i>'
  if absoutdoorhumi > abshumi: todo += ', da die abs. Feuchte drau&szlig;sen h&ouml;her ist, sollte zum ausgleich gel&uuml;ftet werden. <i class="fas fa-door-open"></i>'
 if float(relhumi) >=40 and float(relhumi) <= 60:
  todo += 'An diesem Ort ist die Luftfeuchtigkeit passend. <i class="far fa-thumbs-up"></i>'
 if float(relhumi) > 60:
  todo += 'An diesem Ort ist die Luftfeuuchtigkeit zu hoch'
  if absoutdoorhumi < abshumi: todo += ', da die abs. Feuchte drau&szlig;sen niedriger ist, sollte zum ausgleich gel&uuml;ftet werden. <i class="fas fa-door-open"></i>'
  if absoutdoorhumi > abshumi: todo += ', da die abs. Feuchte drau&szlig;sen h&ouml;her ist, sollte nicht gel&uuml;ftet werden um die Luftfeuchtigkeit m&ouml;glichst zu erhalten. <i class="fas fa-door-closed"></i>'
 return(todo)

##########import config.json
try:
 with open(os.path.split(os.path.abspath(__file__))[0] + '/config.json','r') as file:
  cf = json.loads(file.read())
except:
 sys.exit('exit: The configuration file ' + os.path.split(os.path.abspath(__file__))[0] + '/config.json does not exist or has incorrect content. Please rename the file config.json.example to config.json and change the content as required ')

##########import weather json
from urllib.request import urlopen
url = "http://api.openweathermap.org/data/2.5/weather?" + cf["openweatherlocation"] + "&appid=" + cf["openweatherapikey"] + "&lang=de&units=metric"
response = urlopen(url)
data_weather = json.loads(response.read())
outdoortemp = float(data_weather["main"]["temp"])
outdoorhumi = float(data_weather["main"]["humidity"])
outdoorpres = float(data_weather["main"]["pressure"])
outdoorhuml = calc_abs_humi(outdoorhumi,outdoortemp)

htmlstring = '<!DOCTYPE HTML>\n<!--get awesomefonts from here: https://fontawesome.com/v5.15/icons/cloud-sun?style=solid //-->\n<html>\n<head>'
htmlstring += '<style>\n'
htmlstring += 'h1 {font-size: 3.0rem; background: lightgreen;}\n'
htmlstring += 'h2 {font-size: 2.0rem;}\n'
htmlstring += 'a:link, a:visited, a:hover, a:active {  background-color: lightgray;  color: white;/*  padding: 14px 25px;*/  text-align: center;  text-decoration: none;  display: inline-block;  width: 100%;}\n'
htmlstring += 'html {	font-family: Arial;	display: inline-block;	margin: 0px auto;	text-align: center;}\n'
htmlstring += 'p {	font-size: 3.0rem;}\n'
htmlstring += 'p.small {	font-size: 1.0rem;}\n'
htmlstring += 'table{  margin-left: auto;  margin-right: auto;  border: 1px solid black;  border-collapse: collapse;}\n'
htmlstring += 'td,th,tr {    border: 1px solid black;    border-collapse: collapse;    font-size: 0.8rem;}\n'
htmlstring += 'img {    max-width: 100%;    height: auto;}\n'
htmlstring += '</style>\n'
htmlstring += '<meta charset="utf-8"/>\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">\n</head><body>\n'
htmlstring += '<h1><i class="fas fa-cloud-sun-rain" style="color:CornflowerBlue"></i> Weather</h1><p class="small">' + return_date() + ' ' + return_time()
htmlstring += '</p>\n'

htmlstring += '<table>'
htmlstring += '<tr><th></i>Sensor</th><th>Place</th><th><i class="fas fa-temperature-low"></i></th><th>rel. Feuchte</th><th>abs. Feuchte</th>'
htmlstring += '</tr>'
htmlstring += '<tr><td><i class="fas fa-globe-europe" style="color:lightgreen"></i> OpenWeather</td><td>Internet</td><td>' + str(round(outdoortemp)) + '&deg;C</td><td>' + str(round(outdoorhumi)) + '%</td><td>' + str(round(outdoorhuml)) + 'g/&#13221;</td></tr><tr><td colspan=5>That is the Internet</td></tr>'

for ipchangepart in range(0,255):
	ip = ipareaparts[0] + '.' + ipareaparts[1] + '.' + ipareaparts[2] + '.' + str(ipchangepart)
	mac = get_mac_address(ip=ip)
	if mac != "00:00:00:00:00:00":
		if len(str(mac)) == 17:
			try:
				import urllib.request as urllib2
				import json
				import codecs
				request = urllib2.Request("http://macvendors.co/api/" + mac, headers={'User-Agent' : "API Browser"})
				response = urllib2.urlopen( request )
				reader = codecs.getreader("utf-8")
				obj = json.load(reader(response))
				company = obj['result']['company'];
			except:
				print('unknown vendor: ' + mac)

			if company == 'Espressif Inc.':
				temp = urllib.request.urlopen('http://' + ip + '/temperature').read().decode("UTF-8")
				relhumi = urllib.request.urlopen('http://' + ip + '/humidity').read().decode("UTF-8")
				abshumi = calc_abs_humi(relhumi,temp)
				htmlstring += '<tr><td><i class="fas fa-thermometer-half" style="color:darkblue"></i> ESP01 <small>' + mac[9:] + ' <a href="http://' + ip + '">' + ip + '</a></small></td><td>'
				try:
					htmlstring += cf['place'][mac[9:]]
				except:
					htmlstring += 'unknown'
				htmlstring += '</td><td>' + str(round(float(temp))) + '&deg;C</td><td>' + str(round(float(relhumi))) + '%</td><td>'
				htmlstring += str(round(abshumi))
				htmlstring += 'g/&#13221;</td></tr>'
				htmlstring += '<tr><td colspan="5">'
				htmlstring += return_todo(relhumi,abshumi,outdoorhuml)
				htmlstring += '</td></tr>'

htmlstring += "</table>\n"
htmlstring += "</body>\n</html>\n"
htmlfile.write(htmlstring)
htmlfile.close
