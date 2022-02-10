#!/usr/bin/python3
# Creator: Thiemo Schuff, thiemo@schuff.eu
# Source: https://github.com/Starwhooper/RPi-ESP8266-temphumi-collector
# get awesomefonts from here: https://fontawesome.com/v5.15/icons/cloud-sun?style=solid
# Weather: https://openweathermap.org/api

try: from getmac import get_mac_address
except:
 print('python3 modul getmac is missed')
 print('please do follow command to get it:')
 print('sudo apt-get install python3-pip && sudo pip3 install getmac')
 exit()

try: import json
except:
 print('python3 modul json is missed')
 print('please do follow command to get it:')
 print('sudo apt-get install python3-pip && sudo pip3 install json')
 exit()

import datetime
import os
import socket
import sys
import time
import urllib.request

ip = str((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])
ipareaparts = ip.split('.')

parent_dir = os.path.split(os.path.abspath(__file__))[0]

##########import config.json
try: 
 with open(parent_dir + '/config.json','r') as file: cf = json.loads(file.read())
except: sys.exit('exit: The configuration file ' + parent_dir + '/config.json does not exist or has incorrect content. Please rename the file config.json.example to config.json and change the content as required')

##########check environment
try: htmlfile = open(cf["htmloutput"]["file"],'w')
except: print('file ' + cf["htmloutput"]["file"] + ' not aviable or permission missed')

try: cf["openweather"]["apikey"]
except: sys.exit('exit: no api key in configuration file ' + parent_dir + '/config.json found')

try: os.path.isdir(parent_dir + '/cache')
except:
 try:
  path = os.path.join(parent_dir, 'cache')
  os.mkdir(path)
 except: print('exit, folder ' + parent_dir + '/cache cloud not created')

##########Functions
def calc_abs_humi(relhumi,temp): return(round(10 ** 5 * 18.016 / 8314.3 * relhumi / 100 * 6.1078 * 10**( ( 7.5 * temp ) / ( 237.3 + temp ) ) / ( temp + 273.15 )))
def return_date(): return(datetime.date.today().strftime('%d. %b. \'%y'))
def return_time(): return(time.strftime('%H:%M', time.localtime()))

def return_todo(relhumi,abshumi,absoutdoorhumi,sensoroptions,device):
 sendmsg = False
 todo = ''
 if 'nw;' in sensoroptions:
  todo += cf["htmloutput"]["string_nowindow"]
 else:
  if relhumi < 40:
   todo += cf["htmloutput"]["string_tolesshumi"]
   if absoutdoorhumi < abshumi: todo += cf["htmloutput"]["string_tolesshumi_close"]
   if absoutdoorhumi > abshumi: 
    todo += cf["htmloutput"]["string_tolesshumi_open"]
    sendmsg = True
  if relhumi >=40 and relhumi <= 60: todo += cf["htmloutput"]["string_righthumi"]
  if relhumi > 60:
   todo += cf["htmloutput"]["string_tomuchhumi"]
   if absoutdoorhumi < abshumi: 
    todo += cf["htmloutput"]["string_tomuchhumi_open"]
    sendmsg = True
   if absoutdoorhumi > abshumi: todo += cf["htmloutput"]["string_tomuchhumi_close"]
  if sendmsg == True: 
   pushovermessage(device + ": " + remove_tags(todo))
#   print(todo)
 return(todo)

def is_number(s):
 try:
  float(s)
  return True
 except ValueError:
   return False

def tempdetails(shortmac,temp):
 global cf
 output = ''
 if shortmac in cf['device']:
  if 'sensor' in cf['device'][shortmac]:
   output += '<br /><div class="small">'
   if cf['device'][shortmac]['sensor'] == 'dht11': output += str(round(temp - 2,2)) + ' - ' + str(round(temp + 2,2))
   elif cf['device'][shortmac]['sensor'] == 'dht22': output += str(round(temp - 0.5,2)) + ' - ' + str(round(temp + 0.5,2))
   elif cf['device'][shortmac]['sensor'] == 'sht30': output += str(round(temp - 0.2,2)) + ' - ' + str(round(temp + 0.2,2))
   if cf['device'][shortmac]['sensor'] == 'dht11' and (temp <= 0 or temp >= 60): output += cf["htmloutput"]["string_outside_measuring_range"]
   elif cf['device'][shortmac]['sensor'] == 'dht22' and (temp <= -40 or temp >= 80): output += cf["htmloutput"]["string_outside_measuring_range"]
   output += '</div>'
 return(output)

def relhumidetails(shortmac,relhumi):
 global cf
 output = ''
 if shortmac in cf['device']:
  if 'sensor' in cf['device'][shortmac]:
   output += '<br /><div class="small">'
   if cf['device'][shortmac]['sensor'] == 'dht11': output += str(round(relhumi - 5,2)) + ' - ' + str(round(relhumi + 5,2))
   elif cf['device'][shortmac]['sensor'] == 'dht22': output += str(round(relhumi - 2,2)) + ' - ' + str(round(relhumi + 2,2))
   elif cf['device'][shortmac]['sensor'] == 'sht30': output += str(round(relhumi - 2,2)) + ' - ' + str(round(relhumi + 2,2))
   if cf['device'][shortmac]['sensor'] == 'dht11' and (relhumi <= 20 or relhumi >= 90): output += cf["htmloutput"]["string_outside_measuring_range"]
   elif cf['device'][shortmac]['sensor'] == 'dht22' and (relhumi <= 0 or relhumi >= 100): output += cf["htmloutput"]["string_outside_measuring_range"]
   output += '</div>'
 return(output)

if cf["pushover"]["notification"] == "on":
 import http.client, urllib
 def pushovermessage(message):
  conn = http.client.HTTPSConnection("api.pushover.net:443")
  conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
      "token": cf["pushover"]["apikey"],
      "user": cf["pushover"]["userkey"],
      "message": message,
    }), { "Content-type": "application/x-www-form-urlencoded" })
  conn.getresponse()
 import re
 TAG_RE = re.compile(r'<[^>]+>')
 def remove_tags(text):
  return TAG_RE.sub('', text)

##########import weather json
ow_remotefile = "http://api.openweathermap.org/data/2.5/weather?" + cf["openweather"]["location"] + "&appid=" + cf["openweather"]["apikey"] + "&lang=de&units=metric"
ow_localfile = parent_dir + '/cache/openweathermap.json'

try: owage = os.path.getmtime(ow_localfile)
except: owage = 0

if owage + int(cf["openweather"]["maxageinminutes"]) < time.time():
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

misseddevices = []
for device in cf['device']:
 misseddevices.append(device)

##########generate html output
htmlstring = '<!DOCTYPE HTML><html>\n'
htmlstring += '<head>\n'
htmlstring += '<meta charset="utf-8"/>\n'
htmlstring += '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
htmlstring += '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">\n'
try:
 htmlstring += '<style>\n'
 htmlstring += open(parent_dir + '/format.css','r').read()
 htmlstring += '</style>\n'
except: htmlstring += '<!-- NO STYLE.CSS FOUND //-->\n'
htmlstring += '</head>\n'
htmlstring += '<body>\n'
htmlstring += '<h1><i class="fas fa-cloud-sun-rain" style="color:CornflowerBlue"></i> Weather</h1><p>' + return_date() + ' ' + return_time() + '</p>\n'
htmlstring += '<table>'
htmlstring += '<tr><th></i>Sensor</th><th>Ger&auml;t</th><th><i class="fas fa-temperature-low"></i></th><th>rel. Feuchte</th><th>abs. Feuchte</th><th>Aufgabe</th></tr>'
htmlstring += '<tr><td class="colsensor"><i class="fas fa-globe-europe" style="color:lightgreen"></i> OpenWeather</td><td class="coldevice">Internet</td><td class="coltemp">' + str(round(outdoortemp)) + '&deg;C</td><td class="colrelfeu">' + str(round(outdoorhumi)) + '%</td><td class="colabsfeu">' + str(round(outdoorhuml)) + 'g/&#13221;</td><td class="colcomment"><div class="small">That\'s the Internet at ' + ow_date.strftime("%d. %b. %H:%M") + '</div></td></tr>'

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
    try: os.remove(mv_localfile)
    except: print('no cached file to delete: ' + mv_localfile)

   if company == 'Espressif Inc.':
    shortmac = str(mac)[9:]
    try: sensoroptions = cf['device'][shortmac]['options']
    except: sensoroptions = ''
    if 'i;' in sensoroptions:
     if shortmac in misseddevices:
      misseddevices.remove(shortmac)
     continue

    htmlstringonedevice = ''

    try:
     temp = urllib.request.urlopen('http://' + ip + '/temperature').read().decode("UTF-8")
     relhumi = urllib.request.urlopen('http://' + ip + '/humidity').read().decode("UTF-8")
    except:
     temp = 'error'
     relhume = 'error'
     print("Device " + ip + " known on DHCP, but provide no information about temperatur or humidity")

    if is_number(relhumi) and is_number(temp):
     try: sensorlabel = cf['device'][shortmac]['label']
     except: sensorlabel = 'unknown'
     temp = float(temp)
     relhumi = float(relhumi)
     abshumi = calc_abs_humi(relhumi,temp)
#     try: sensoroptions = cf['device'][shortmac]['options']
#     except: sensoroptions = ''
     
     htmlstringonedevice += '<tr><td class="colsensor"><i class="fas fa-thermometer-half" style="color:darkblue"></i> Espressif <div class="small">' + shortmac + ' <a href="http://' + ip + '">' + ip + '</a></div></td><td class="coldevice">'
     htmlstringonedevice += sensorlabel
     htmlstringonedevice += '</td><td class="coltemp">'
     htmlstringonedevice += str(round(temp,2)) + '&deg;C'
     htmlstringonedevice += tempdetails(shortmac,temp)
     htmlstringonedevice += '</td><td class="colrelfeu">'
     htmlstringonedevice += str(round(relhumi)) + '%'
     htmlstringonedevice += relhumidetails(shortmac,relhumi)
     htmlstringonedevice += '</td><td class="colabsfeu">'
     htmlstringonedevice += str(round(abshumi)) + 'g/&#13221;'
     htmlstringonedevice += '</td>'
     htmlstringonedevice += '<td class="colcomment">'
     htmlstringonedevice += str(return_todo(relhumi,abshumi,outdoorhuml,sensoroptions,sensorlabel))
     htmlstringonedevice += '</td></tr>'
     if shortmac in misseddevices:
      misseddevices.remove(shortmac)
    htmlstring +=  htmlstringonedevice

for misseddevice in misseddevices:
 htmlstring += '<tr><td class="errorleft"><i class="fas fa-exclamation-triangle" style="color:red"></i> ' + misseddevice + '</td><td class="errormiddle">'
 try: sensorlabel = cf['device'][misseddevice]['label']
 except: sensorlabel = 'unknown'
 htmlstring += sensorlabel
 htmlstring += '</td><td  class="errorright" colspan=4 >' + cf['htmloutput']['string_configured_but_not_found'] + '</td></tr>'

htmlstring += "</table>\n"

htmlstring += "</body>\n</html>\n"
htmlfile.write(htmlstring)
htmlfile.close
