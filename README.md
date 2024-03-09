### Installation

```
sudo apt-get update
sudo apt-get upgrade
sudo rm /usr/lib/python3.11/EXTERNALLY-MANAGED
sudo apt-get install pigpio python-pigpio python3-pigpio
pip3 install adafruit-circuitpython-lsm6ds adafruit-circuitpython-lps2x adafruit-circuitpython-bno055 python-socketio eventlet flask-socketio gevent gevent-websocket
sudo apt install -y python3-picamera2 --no-install-recommends
sudo systemctl enable pigpiod
sudo pigpiod
```

### Generate ssl keys

```
openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=192.168.50.129"
```

### Examples

```
from .drivers.lps2x.py import Barometer, BAROMETER_TYPE

barometer = Barometer(BAROMETER_TYPE.LPS22)

print(barometer.getPressure())
print(barometer.getTemperature())
```

```
from .drivers.altimu10v5 import Altimu10V5

sensor = Altimu10V5()

print(sensor.getData())

```
