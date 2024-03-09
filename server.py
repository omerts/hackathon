import socketio
import time
import gevent
import board
from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import numpy as np
from drivers.servo import Servo
from drivers.lps2x_full import LPS22
from drivers.camera import Camera

allow_launch = False

app = Flask(__name__, static_folder='fe', static_url_path='')
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='gevent')
servo = Servo(18)
barometer = LPS22(board.I2C())
camera = Camera()

def calculate_altitude(pressure_hpa, temperature_c):
    # Constants
    temp_kelvin = temperature_c + 273.15  # Convert temperature to Kelvin
    sea_level_pressure = 1013.25  # Sea level standard atmospheric pressure in hPa
    gravitational_acceleration = 9.80665  # Acceleration due to gravity in m/s^2
    molar_mass_air = 0.0289644  # Molar mass of Earth's air in kg/mol
    universal_gas_constant = 8.3144598  # Universal gas constant in J/(mol*K)

    # Barometric formula
    altitude = ((universal_gas_constant * temp_kelvin) / (gravitational_acceleration * molar_mass_air)) \
        * np.log(sea_level_pressure / pressure_hpa) # In meters

    return altitude

def send_status(parachute_armed, parachute_deployed, is_launched = False):
    socketio.emit('status', { 'parachuteArmed': parachute_armed, 'parachuteDeployed': parachute_deployed, 'isLaunched': is_launched})

def send_rocket_data(altitude):
    socketio.emit('rocket-data', { 'timestamp': time.time(), 'altitude': altitude})
    
# Event handler for new connections
@socketio.event
def connect():
    print('Client connected')

# Event handler for messages
@socketio.event
def message(sid, data):
    print('message ', data)
    socketio.send(sid, f"Reply: {data}")

# Event handler for disconnections
@socketio.event
def disconnect():
    print('client disconnected')

@socketio.on('arm-parachute')
def arm_parachute():
    print('arm-parachute')

    camera.start()

    send_status(True, False)

@socketio.on('disarm-parachute')
def arm_parachute():
    print('disarm-parachute')

    send_status(False, False)

@socketio.on('reset-parachute')
def arm_parachute():
    print('reset-parachute')

    send_status(False, False)

@socketio.on('deploy-parachute')
def arm_parachute():
    print('deploy-parachute')

    send_status(True, True)

@socketio.on('launch')
def launch():
    print('launch')
    send_status(True, True, True)
    
    global allow_launch 

    allow_launch = True
    gevent.sleep(5)
    
    if allow_launch:
        servo.right()
        gevent.sleep(2)
        servo.stop()
        allow_launch = False

@socketio.on('abort-launch')
def cancel_launch():
    print('abort launch')
    global allow_launch 
    allow_launch = False

def read_and_send_data():
    while True:
        print(barometer.pressure, barometer.temperature)
        send_rocket_data(1)
        gevent.sleep(1) # Send data every 1 second, change this

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    try:
        gevent.spawn(read_and_send_data)

        context = ('cert.pem', 'key.pem')
        socketio.run(app, port=5000, host='0.0.0.0', debug=False, ssl_context=context)
    except KeyboardInterrupt:
        camera.stop()