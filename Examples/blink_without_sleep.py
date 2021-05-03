# Blink Without Sleep

from machine import Pin
from time import ticks_ms

led_pin = 25

def setup():
    global led
    led = Pin(led_pin, Pin.OUT)

def main():
    setup()
    
    time_to_blink = 0
    interval_ms = 500 # miliseconds
    led_is_on = True
    
    while True:
        if ticks_ms() >= time_to_blink:
            led.value(led_is_on)
            led_is_on = not led_is_on
            time_to_blink = ticks_ms() + interval_ms
