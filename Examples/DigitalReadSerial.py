# MicroPython Cheatsheet

from machine import Pin
from time import sleep

button_pin = 12 # Connect one of the pushbutton leads to this Pi Pico pin and the other lead to GND (ground).

def setup():
    global button
    button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

def main():
    setup()
    while True:
        print(button.value())
        sleep(1)
