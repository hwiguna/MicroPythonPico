def main():
    from machine import Pin, I2C
    from ssd1306 import SSD1306_I2C

    i2c=I2C(1,sda=Pin(2), scl=Pin(3), freq=400000)
    oled = SSD1306_I2C(128, 64, i2c)

    oled.text("Hello Tom's", 0, 0)
    oled.show()
