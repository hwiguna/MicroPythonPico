# Fade

from machine import Pin, PWM
from time import sleep

led_pin = 25

def setup():
    global pwm_led
    led = Pin(led_pin, Pin.OUT)
    pwm_led = PWM(led)
    pwm_led.freq(500)

def main():
    setup()
    
    brightness = 0
    max_brightness = 65535
    fade_amount=int(max_brightness/100) # Divide by larger# for finer steps
    while True:
        pwm_led.duty_u16(brightness) # ranges from 0 to 65535
        brightness = brightness + fade_amount
        if brightness <= 0 or brightness >= max_brightness:
            fade_amount = -fade_amount
        
        sleep(0.01) # Decrease sleep for faster fade rate

