# Debounce

from machine import Pin
from time import sleep_ms

button_pin = 13 # Connect one of the pushbutton leads to this Pi Pico pin and the other lead to GND (ground).

def setup():
    global button
    button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

def wait_button_release(button):
    while button.value() == 0:
        sleep_ms(20)

def is_button_pressed(button):
    is_pressed = button.value() == 0
    if is_pressed:
        #wait_button_release(button) # Uncomment this line if you want to wait till button is released
        sleep_ms(200) # Uncomment this line if you want to repeat as the button is continually pressed
    return is_pressed

def main():
    setup()
    count=0
    while True:
        if is_button_pressed(button):
            count += 1
            print(count)

