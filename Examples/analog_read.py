from machine import Pin, ADC
from time import sleep

analog_pin = 26 # Connect middle lead of potentiomenter to this pin, one outer pin to 3V3, other outer pin to GND

def setup():
    global analog
    analog = ADC(analog_pin)

def main():
    setup()
    while True:
        print(analog.read_u16()) # Ranges from 0 to 65535
        sleep(.5)
