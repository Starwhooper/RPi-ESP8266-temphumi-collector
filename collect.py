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

parent_dir = os.path.split(os.path.abspath(__file__))[0]

##########import config.json
try:
 with open(parent_dir + '/config.json','r') as file:
  cf = json.loads(file.read())
except: sys.exit('exit: The configuration file ' + parent_dir + '/config.json does not exist or has incorrect content. Please rename the file config.json.example to config.json and change the content as required')

##########check environment
try: htmlfile = open(cf["htmloutput"]["file"],'w')
except: print('file ' + cf["htmloutput"]["file"] + ' not aviable or permission missed')

try: cf["openweatherlocation"]
except: sys.exit('exit: no api key in configuration file ' + parent_dir + '/config.json found')

try: os.path.isdir(parent_dir + '/cache')
except:
	try:
		path = os.path.join(parent_dir, 'cache')
		os.mkdir(path)
	except: print('exit, folder ' + parent_dir + '/cache cloud not created')

##########Functions
def calc_abs_humi(relhumi,temp): return(round(10 ** 5 * 18.016 / 8314.3 * float(relhumi) / 100 * 6.1078 * 10**( ( 7.5 * float(temp) ) / ( 237.3 + float(temp) ) ) / ( float(temp) + 273.15 )))
def return_date(): return(datetime.date.today().strftime('%d. %b. \'%y'))
def return_time(): return(time.strftime('%H:%M', time.localtime()))

def return_todo(relhumi,abshumi,absoutdoorhumi):
 todo = ''
 if float(relhumi) < 40:
  todo += cf["htmloutput"]["string_tolesshumi"]
  if absoutdoorhumi < abshumi: todo += cf["htmloutput"]["string_tolesshumi_close"]
  if absoutdoorhumi > abshumi: todo += cf["htmloutput"]["string_tolesshumi_open"]
 if float(relhumi) >=40 and float(relhumi) <= 60: todo += cf["htmloutput"]["string_righthumi"]
 if float(relhumi) > 60:
  todo += cf["htmloutput"]["string_tomuchhumi"]
  if absoutdoorhumi < abshumi: todo += cf["htmloutput"]["string_tomuchhumi_open"]
  if absoutdoorhumi > abshumi: todo += cf["htmloutput"]["string_tomuchhumi_close"]
 return(todo)

##########import weather json
ow_remotefile = "http://api.openweathermap.org/data/2.5/weather?" + cf["openweatherlocation"] + "&appid=" + cf["openweatherapikey"] + "&lang=de&units=metric"
ow_localfile = parent_dir + '/cache/openweathermap.json'

try: owage = os.path.getmtime(ow_localfile)
except: owage = 0

if owage + 60*30 < time.time():
	from urllib.request import urlopen
	urllib.request.urlretrieve(ow_remotefile, ow_localfile)

openweatherjson = open(ow_localfile,)
data_weather = json.loads(openweatherjson.read())
openweatherjson.close()

outdoortemp = float(data_weather["main"]["temp"])
outdoorhumi = float(data_weather["main"]["humidity"])
outdoorpres = float(data_weather["main"]["pressure"])
outdoorhuml = calc_abs_humi(outdoorhumi,outdoortemp)
ow_date = datetime.datetime.fromtimestamp(data_weather["dt"])

htmlstring = '<!DOCTYPE HTML><html>\n'
htmlstring += '<head>\n'
try:
	htmlstring += '<style>\n'
	htmlstring += open('style.css','r').read()
	htmlstring += '</style>\n'
except: htmlstring += '<!-- NO STYLE.CSS FOUND //-->\n'

htmlstring += '<meta charset="utf-8"/>\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">\n</head><body>\n'
htmlstring += '<h1><i class="fas fa-cloud-sun-rain" style="color:CornflowerBlue"></i> Weather</h1><p class="small">' + return_date() + ' ' + return_time()
htmlstring += '</p>\n'
htmlstring += '<table>'
htmlstring += '<tr><th></i>Sensor</th><th>Place</th><th><i class="fas fa-temperature-low"></i></th><th>rel. Feuchte</th><th>abs. Feuchte</th>'
htmlstring += '</tr>'
htmlstring += '<tr><td><i class="fas fa-globe-europe" style="color:lightgreen"></i> OpenWeather</td><td>Internet</td><td>' + str(round(outdoortemp)) + '&deg;C</td><td>' + str(round(outdoorhumi)) + '%</td><td>' + str(round(outdoorhuml)) + 'g/&#13221;</td></tr><tr><td colspan=5>That\'s the Internet at ' + ow_date.strftime("%d. %b. %H:%M") + '</td></tr>'

for ipchangepart in range(0,255):
	ip = ipareaparts[0] + '.' + ipareaparts[1] + '.' + ipareaparts[2] + '.' + str(ipchangepart)
	mac = get_mac_address(ip=ip)
	if mac != "00:00:00:00:00:00":
		if len(str(mac)) == 17:
			mv_remotefile = "http://macvendors.co/api/" + mac
			mv_localfile = parent_dir + '/cache/' + mac + '.json'
			try:
				try: os.path.getmtime(mv_localfile)
				except: urllib.request.urlretrieve(mv_remotefile, mv_localfile)
				macjson = open(mv_localfile,)
				data_mac = json.loads(macjson.read())
				macjson.close()
				company = data_mac['result']['company'];
			except:
				print('unknown vendor: ' + mac)
				os.remove(mv_localfile)

			if company == 'Espressif Inc.':
				temp = urllib.request.urlopen('http://' + ip + '/temperature').read().decode("UTF-8")
				relhumi = urllib.request.urlopen('http://' + ip + '/humidity').read().decode("UTF-8")
				abshumi = calc_abs_humi(relhumi,temp)
				htmlstring += '<tr><td><i class="fas fa-thermometer-half" style="color:darkblue"></i> Espressif <small>' + mac[9:] + ' <a href="http://' + ip + '">' + ip + '</a></small></td><td>'
				try: htmlstring += cf['place'][mac[9:]]
				except: htmlstring += 'unknown'
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
