from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from utime import sleep

a = [(0,0),(0,1),(1,2),(2,3),(3,3)]
b = [(0,0),(1,0),(2,1),(3,2),(3,3)]
c = [(3,0),(3,1),(2,2),(1,3),(0,3)]
d = [(3,0),(2,0),(1,1),(0,2),(0,3)]

lefts = [(a,0),(c,0),(d,1),(b,1)] # Snake going left, head is on left
rights = [(c,3),(a,3),(b,2),(d,2)] # Snake going right, head is on right
ups = [(c,1),(b,1),(a,2),(d,2)] # Snake going up, head is on top
downs=[(d,3),(a,3),(b,0),(c,0)] # Snake going down, head is on bottom

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

def erasee(x,y,e):
    if e[1]==0: erase(x,y,e[0])
    if e[1]==1: erase(x,y-1,e[0])
    if e[1]==2: erase(x-1,y-1,e[0])
    if e[1]==3: erase(x-1,y,e[0])

def left_to_right(y):
    x=0
    for r in range(6):
        for e in lefts:
            drawe(x,y,e)
            oled.show()
            sleep(t)
            x += 1

def right_to_left(y):
    x=int(127/3)
    for r in range(6):
        for e in rights:
            drawe(x,y,e)
            oled.show()
            sleep(t)
            x -= 1

def go_up(x):
    y=int(64/3)
    for r in range(6):
        for e in ups:
            drawe(x,y,e)
            oled.show()
            sleep(t)
            y -= 1

def go_down(x):
    y=0
    for r in range(6):
        for e in downs:
            drawe(x,y,e)
            oled.show()
            sleep(t)
            y += 1

def next_right(old_head):
    for e in rights:
        if e[0]==old_head[0]:
            print("wow")
    return old_head
    
def move_snake(dx,dy):
    # at any rate, remove tail
    print(len(snake))
    tail = snake[-1]
    erasee(tail[0],tail[1],tail[2])
    snake.pop()  
    if dx==1:
        old_head = snake[0]
        new_head = next_right(old_head)
        snake.insert(0,new_head)
    
def main():
    sleep(0.5)
    i2c=I2C(1,sda=Pin(2), scl=Pin(3), freq=400000)
    global oled
    oled = SSD1306_I2C(128, 64, i2c)

    oled.fill(0)
#    go_up(1)
#     go_down(3)
#     left_to_right(1)
#     right_to_left(3)

    x=int(128/3/2)
    y=int(64/3/2)
    global snake
    snake = [ (x,y,rights[0]), (x-1,y,rights[1]), (x-2,y,rights[2]), (x-3,y,rights[3])]
    
    for r in range(2):
        for sn in snake:
            drawe(sn[0],sn[1],sn[2])
            oled.show()
        sleep(1)
        move_snake(1,0)
        oled.show()

    sleep(t)

#main()
    
