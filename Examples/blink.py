# Blink

from machine import Pin
from time import sleep

led_pin = 25

def setup():
    global led
    led = Pin(led_pin, Pin.OUT)

def main():
    setup()
    while True:
        led.value(1)
        sleep(1)
    
        led.value(0)
        sleep(1)
