# Button

from machine import Pin
from time import sleep

led_pin = 25
button_pin = 12 # Connect one of the pushbutton leads to this Pi Pico pin and the other lead to GND (ground).

def setup():
    global led
    led = Pin(led_pin, Pin.OUT)

    global button
    button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

def main():
    setup()
    while True:
        is_button_pressed = button.value() == 0
        led.value(not is_button_pressed)
        sleep(0.1)

