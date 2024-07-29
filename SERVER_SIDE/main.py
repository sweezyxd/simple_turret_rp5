from gpiozero import DigitalOutputDevice
from gpiox_pwm import PWM
from server import SERVER
import time
import cv2
import numpy as np
from picamera2 import Picamera2

width, height = 640, 480
global servo_1, servo_2
global on
on = True

def checkKey(key):
    if key == "p":
        on = False
    ApplyKeyX(key)
    ApplyKeyY(key)
        


def ApplyKeyX(key):
    #Applying X axis movement
    if key == "d":
        servo_1.setPulse(1.425)
    elif key == "a":
        servo_1.setPulse(1.53)
    else:
        servo_1.setPulse(1.500)

def ApplyKeyY(key):
    current = servo_2.current_pulse_func()
    max_pulse, min_pulse = servo_2.max_pulse, servo_2.min_pulse

    if key == "s":
        if current != None and current <= max_pulse:
            servo_2.setPulse(current + 0.020)

    elif key == "w":
        if current != None and current >= min_pulse:
            servo_2.setPulse(current - .020)

# Setting up Servos
servo_1 = PWM(19, 2.5, 0.5, 20) # X
servo_2 = PWM(18, 2.5, 0.5, 20) # Y
red_led = DigitalOutputDevice(13)
red_led.value = 1
servo_1.start()
servo_2.start()
servo_2.setPulse(1.5)

# Setting up Server
server = SERVER("192.168.192.168", 5050, "1234", (height, width, 3), 65000, checkKey)
server.start()

#Setting up Camera
picam = Picamera2()
picam.configure(picam.create_still_configuration(main={"size": (width, height)}, controls={"ExposureTime": 10000, "AnalogueGain": 2}))
picam.start()
print("STARTED")
while on:
    frame = picam.capture_array()
    #SEND FRAME HERE:
    server.setFrame(frame)
    time.sleep(0.005)

server.close()
servo_1.stop()
servo_2.stop()
