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
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout private.key -out certificate.crt
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
