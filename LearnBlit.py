def main():
    from machine import Pin, I2C
    from ssd1306 import SSD1306_I2C
    import framebuf

    i2c=I2C(1,sda=Pin(2), scl=Pin(3), freq=400000)
    oled = SSD1306_I2C(128, 64, i2c)

    oled.text("----- Tom's", 0, 0)
    oled.show()

    b2=bytearray(40)
    b2[0]=255
    b2[1]=0
    b2[2]=0
    b2[3]=255
    fb = framebuf.FrameBuffer(b2, 5,8, framebuf.MVLSB)
    oled.blit(fb,20,0)
    oled.show()