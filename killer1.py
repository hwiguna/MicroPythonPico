def main():
    from machine import Pin, I2C
    from ssd1306 import SSD1306_I2C
    from utime import sleep

    i2c=I2C(1,sda=Pin(2), scl=Pin(3), freq=400000)
    oled = SSD1306_I2C(128, 64, i2c)

    points = [\
        (9,11),(10,11),(11,11),
        (12,12),\
        (13,13),(13,14),(13,15),\
        (14,16),\
        (15,17),(16,17),(17,17),\
        (18,16),\
        (19,15),(19,14),(19,13),\
        (20,12)]
    
    for snake in range(5):
            for p in points:
                oled.pixel(snake*(20-9)+p[0],p[1], 0)
                oled.show()
            sleep(.005)    