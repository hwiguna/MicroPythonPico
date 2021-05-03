from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from utime import sleep

a = [(0,0),(0,1),(1,2),(2,3),(3,3)]
b = [(0,0),(1,0),(2,1),(3,2),(3,3)]
c = [(3,0),(3,1),(2,2),(1,3),(0,3)]
d = [(3,0),(2,0),(1,1),(0,2),(0,3)]

lr = [(a,0),(c,0),(d,1),(b,1)]
rl = [(c,3),(a,3),(b,2),(d,2)]
up = [(c,1),(b,1),(a,2),(d,2)]
down=[(d,3),(a,3),(b,0),(c,0)]

snake = []

t=.05

def plot(c,r,a,isDraw):
    for p in a:
        oled.pixel(c*3+p[0],63-r*3-p[1],1 if isDraw else 0)

def draw(c,r,a):
    plot(c,r,a,True)

def erase(c,r,a):
    plot(c,r,a,False)

def drawe(x,y,e):
    if e[1]==0: draw(x,y,e[0])
    if e[1]==1: draw(x,y-1,e[0])
    if e[1]==2: draw(x-1,y-1,e[0])
    if e[1]==3: draw(x-1,y,e[0])

def left_to_right(y):
    x=0
    for r in range(6):
        for e in lr:
            drawe(x,y,e)
            oled.show()
            sleep(t)
            x += 1

def right_to_left(y):
    x=int(127/3)
    for r in range(6):
        for e in rl:
            drawe(x,y,e)
            oled.show()
            sleep(t)
            x -= 1

def go_up(x):
    y=int(64/3)
    for r in range(6):
        for e in up:
            drawe(x,y,e)
            oled.show()
            sleep(t)
            y -= 1

def go_down(x):
    y=0
    for r in range(6):
        for e in down:
            drawe(x,y,e)
            oled.show()
            sleep(t)
            y += 1

def main():
    i2c=I2C(1,sda=Pin(2), scl=Pin(3), freq=400000)
    global oled
    oled = SSD1306_I2C(128, 64, i2c)

    oled.fill(0)
    go_up(1)
    go_down(3)
    left_to_right(1)
    right_to_left(3)

#main()
