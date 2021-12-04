# RPI-ESP8266-temphumi-collector
Detect ESP8266 by itself, try to grep the weather information and publish it to website

It also use API from https://macvendors.co

The information from booth sources will be cached, to reduce the workload

![Display](https://github.com/Starwhooper/RPi-ESP8266-temphumi-collector/blob/master/examples/wetter.png)

## install ##
```bash
cd /opt
sudo apt-get install python3-pip && sudo pip3 install getmac
sudo git clone https://github.com/Starwhooper/RPi-ESP8266-temphumi-collector
sudo chmod +x /opt/RPi-ESP8266-temphumi-collector/collect.py
sudo mkdir /opt/RPi-ESP8266-temphumi-collector/cache
```

## Update ##
If you already use it, feel free to update with
```bash
cd /opt/RPi-ESP8266-temphumi-collector
sudo git pull origin main
```

## Configure ##
copy example configuration at first time:
```bash
cp /opt/RPi-ESP8266-temphumi-collector/config.json.example /opt/RPi-ESP8266-temphumi-collector/config.json
```

edit config file
It use API from https://openweathermap.org, please add you API Key in config.json
```bash
sudo nano /opt/RPi-ESP8266-temphumi-collector/config.json
```

## start ##
add to cronjob
```bash
sudo crontab -e
*/5 * * * * /opt/RPi-ESP8266-temphumi-collector/collect.py
```


