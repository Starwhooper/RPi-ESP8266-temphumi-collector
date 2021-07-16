#!/usr/bin/python3
# Creator: Thiemo Schuff, thiemo@schuff.eu
# Source: https://github.com/Starwhooper/RPi-ESP8266-temphumi-collector

try: from getmac import get_mac_address
except:
	print('python3 modul getmac is missed')
	print('please do follow command to get it')
	print(' ')
	print('sudo apt-get install python3-pip && sudo pip3 install getmac')
	exit()

import urllib.request
import socket
import datetime
import time
import os

ip = str((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])
ipareaparts = ip.split('.')

try: htmlfile = open('/var/www/html/house.html','w')
except:
	print('file /var/www/html/house.html not aviable of permission missed')
	print('please do follow command to get it')
	print(' ')
	print('sudo touch /var/www/html/house.html && sudo chmod 777 /var/www/html/house.html')

htmlstring = "<!DOCTYPE HTML>"
htmlstring = '<html lang="en">\n'
htmlstring += "<head>\n"
htmlstring += '<meta charset="utf-8"/>\n'
htmlstring += "</head>\n"
htmlstring += "<body>\n"
htmlstring += "<p>Date:" + datetime.date.today().strftime('%a')[:2] + datetime.date.today().strftime(', %d. %b.\'%y') + "</p>\n"
htmlstring += "<p>Time:" + time.strftime('%H:%M:%S', time.localtime()) + "</p>\n"

for ipchangepart in range(0,255):
	ip = ipareaparts[0] + '.' + ipareaparts[1] + '.' + ipareaparts[2] + '.' + str(ipchangepart)
	mac = get_mac_address(ip=ip)
	if mac != "00:00:00:00:00:00":
		if len(str(mac)) == 17:
			if str(mac[:8]) == "e8:db:84":
#				print("detect: " + ip)
				temp = urllib.request.urlopen('http://' + ip + '/temperature').read().decode("UTF-8")
				humi = urllib.request.urlopen('http://' + ip + '/humidity').read().decode("UTF-8")
				htmlstring += "<h2>Sensor ESP8266 + DHT 1.11 " + mac[9:] + "</h2>\n"
				htmlstring += '<p>IP: <a href="http://' + ip + '">' + ip + '</a></p>\n'
				htmlstring += "<p>Temperatur: " + temp + "&deg;C<br/>Luftfeuchtigkeit: " + humi + "%</p>\n"

			if str(mac[:8]) == "f0:00:00":
				htmlstring += "<h2>SV3C Camera (A-Series) " + mac[9:] + "</h2>\n"
				htmlstring += '<p>IP: <a href="http://' + ip + '">' + ip + '</a></p>\n'
				videoin = 'rtsp://' + ip + '/stream1'
				videoout = '/var/www/html/camimages/' + mac.replace(':', '') + '-output.jpg'
				os.system('ffmpeg -y -i ' + videoin + ' -ss 5 -vf scale=600:-1 -frames:v 1 ' + videoout)
				htmlstring += '<p><img src="camimages/' + mac.replace(':', '') + '-output.jpg"></p>\n'

			if str(mac[:8]) == "00:e0:59":
				htmlstring += "<h2>SV3C Camera (HX-Series) " + mac[9:] + "</h2>\n"
				htmlstring += '<p>IP: <a href="http://' + ip + '/web/admin.html">' + ip + '</a></p>\n'
				videoin = 'rtsp://' + ip + ':554/12'
				videoout = '/var/www/html/camimages/' + mac.replace(':', '') + '-output.jpg'
				os.system('ffmpeg -y -i ' + videoin + ' -ss 5 -vf scale=600:-1 -frames:v 1 ' + videoout)
				htmlstring += '<p><img src="camimages/' + mac.replace(':', '') + '-output.jpg"></p>\n'

htmlstring += "</body>\n"
htmlstring += "</html>\n"
htmlfile.write(htmlstring)
htmlfile.close
