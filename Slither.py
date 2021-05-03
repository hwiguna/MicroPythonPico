# Connect 128x64 OLED SDA to GPIO 2, SCL to GPIO 3
# Pushbuttons are on GPIO 12,13,14, and 15 (see setupIO below) to ground. Uses internal pullup resistor.

#== Imports ==
import time, random
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

#== Globals ==
#-- OLED --
BUS,SDA,SCL = 1, 2,3
WIDTH, HEIGHT = 128, 64

#-- Game Arena --
unit = 4
border=2
titleHeight=9
# Note that arenaWidth and arenaHeight is one unit less than actual and must be multiple of unit.
arenaWidth = int((WIDTH-border-border-unit)/unit)
arenaHeight = int((HEIGHT-titleHeight-border-border-unit)/unit)

def setupOled():
    global oled
    i2c = I2C(BUS, sda=Pin(SDA), scl=Pin(SCL), freq=400000)
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
    oled.fill(0)

def setupIO():
    global buttonRight, buttonLeft, buttonUp, buttonDown
    buttonRight = Pin(13, Pin.IN, Pin.PULL_UP)
    buttonLeft = Pin(14, Pin.IN, Pin.PULL_UP)
    buttonUp = Pin(15, Pin.IN, Pin.PULL_UP)
    buttonDown = Pin(12, Pin.IN, Pin.PULL_UP)

def draw_frame():
    oled.fill(0)
    oled.text(str(length_of_snake-1), 100,0)  
    oled.text('Slither',0,0)
    oled.rect(border,titleHeight+border, (arenaWidth+1)*unit, (arenaHeight+1)*unit, 1) # Inner Border
    oled.rect(0,titleHeight, (arenaWidth+1)*unit+2*border, (arenaHeight+1)*unit+2*border, 1) # Outer border
   
def game_over():
    oled.text('Game Over',30,int(HEIGHT/2), 1)
    oled.show()

def wait_for_any_buttons():
    while buttonRight.value()==1 and \
          buttonLeft.value()==1 and \
          buttonUp.value()==1 and \
          buttonDown.value()==1:
        time.sleep(.1)

def reset():
    global x1
    x1 = int(arenaWidth/2)
    
    global y1
    y1 = int(arenaHeight/2)
    
    make_food()
    
    global x1_change
    x1_change = 1
    
    global y1_change
    y1_change = 0
    
    global snake_list
    snake_list = []
    
    global length_of_snake
    length_of_snake = 3
    
    global snake
    snake = [[x1,y1], [x1,y1], [x1,y1]]
    
    global is_game_over
    is_game_over = False

def make_food():
    global food
    food = [ random.randrange(arenaWidth), random.randrange(arenaHeight) ]

def draw_food():
    oled.rect(border+food[0]*unit,titleHeight+border+food[1]*unit,unit,unit, 1)

def move_snake():
    global x1,y1, x1_change, y1_change, snake_list, length_of_snake
    global food, is_game_over
    
    if buttonDown.value()==0:
        y1_change = 1
        x1_change = 0
    elif buttonUp.value()==0:
        y1_change = -1
        x1_change = 0
    elif buttonRight.value()==0:
        y1_change = 0
        x1_change = 1
    elif buttonLeft.value()==0:
        y1_change = 0
        x1_change = -1

    x1 += x1_change
    y1 += y1_change

    # Did snake run into arena wall?
    if x1 > arenaWidth or x1 < 0 or y1 > arenaHeight or y1 < 0:
        print("run into wall")
        print(x1,arenaWidth, " ", y1,arenaHeight)
        is_game_over = True

    # Did snake eat something?
    if (x1 == food[0] and y1 == food[1]):
        make_food()
        length_of_snake +=1

    # Add new head, remove last tail
    snakehead = [x1,y1]
    snake_list.append(snakehead)
    if len(snake_list) > length_of_snake:
        del snake_list[0]

    # Did snake run into himself?
    for x in snake_list[:-1]:
        if x == snakehead:
            print("run into self")
            is_game_over = True

def draw_snake():   
    for x in snake_list:
        print("draw snake at", x[0], x[1])
        oled.rect(border+x[0]*unit,titleHeight+border+x[1]*unit,unit,unit, 1)    

def main():
    setupOled()
    setupIO()

    while True:
        reset()
        draw_frame()
        oled.text('Press to Start',8,int(HEIGHT/2), 1)
        oled.show()
        wait_for_any_buttons()

        while not is_game_over:
            draw_frame()
            draw_food()
            move_snake()
            draw_snake()
            oled.show()
            time.sleep_ms(100)
            
        game_over()
        wait_for_any_buttons()
