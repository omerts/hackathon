import socketio
import time
import gevent
import board
import os
from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import numpy as np
from drivers.servo import Servo
from drivers.lps2x_full import LPS22
from drivers.camera import Camera
from logger import logger

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
    logger.info('Client connected')

# Event handler for messages
@socketio.event
def message(data):
    logger.info('message ', data)

# Event handler for disconnections
@socketio.event
def disconnect():
    logger.info('client disconnected')

@socketio.on('arm-parachute')
def arm_parachute():
    logger.info('arm-parachute')

    camera.start()

    send_status(True, False)

@socketio.on('disarm-parachute')
def arm_parachute():
    logger.info('disarm-parachute')

    camera.stop()

    send_status(False, False)

@socketio.on('reset-parachute')
def reset_parachute():
    logger.info('reset-parachute')

    send_status(False, False)

@socketio.on('deploy-parachute')
def deploy_parachute():
    logger.info('deploy-parachute')

    send_status(True, True)

@socketio.on('launch')
def launch():
    logger.info('launch')
    send_status(True, True, True)
    
    global allow_launch 

    allow_launch = True
    gevent.sleep(5)
    
    if allow_launch:
        logger.info('Running servo')
        servo.right()
        gevent.sleep(2)
        servo.stop()
        allow_launch = False
    else:
        logger.info('Aborted servo due to abort command')


@socketio.on('abort-launch')
def abort_launch():
    logger.info('abort launch')
    global allow_launch 
    allow_launch = False
    camera.stop()
    send_status(False, False, False)

def read_and_send_data():
    while True:
        altitude = calculate_altitude(barometer.pressure, barometer.temperature)
        logger.info(f"Altitude: {altitude}")
        send_rocket_data(altitude)
        gevent.sleep(0.2) # Send data every 1 second, change this

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    try:
        gevent.spawn(read_and_send_data)
        current_directory = os.path.dirname(os.path.abspath(__file__))
        ssl_cert_path = os.path.join(current_directory, 'certificate.crt')
        ssl_key_path = os.path.join(current_directory, 'private.key')

        socketio.run(app, port=5000, host='0.0.0.0', debug=False, certfile=ssl_cert_path, keyfile=ssl_key_path)
    except KeyboardInterrupt:
        camera.stop()