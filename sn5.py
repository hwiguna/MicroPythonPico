from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from utime import sleep


#=== SPRITES ===
# ..XX  ...X  XX..  X...
# .X..  ...X  ..X.  X...
# X...  ..X.  ...X  .X..
# X...  XX..  ...X  ..XX
# a     b     c     d      
a = [(0,0),(0,1),(1,2),(2,3),(3,3)]
b = [(0,0),(1,0),(2,1),(3,2),(3,3)]
c = [(3,0),(3,1),(2,2),(1,3),(0,3)]
d = [(3,0),(2,0),(1,1),(0,2),(0,3)]

horzSeq = "d--b--a-=c-=d--" #Left to Right (positive direction curve down first)
vertSeq = "b=-c=-d--a--b=-" #Bottom to top (positive direction curve right first)

snake = []
scale = 1
spd = .2 #0.05

def plot(x,y,sprite,isDraw):
    for p in sprite:
        oled.rect(x*3*scale+p[0]*scale,63-y*3*scale-p[1]*scale, scale,scale, 1 if isDraw else 0)

def draw(c,r,a):
    plot(c,r,a,True)

def erase(c,r,a):
    plot(c,r,a,False)

def toSprite(spriteName):
    sprite = d
    if spriteName=='a': sprite = a
    if spriteName=='b': sprite = b
    if spriteName=='c': sprite = c
    return sprite

def toOffset(offsetSymbol):
    result = 0
    if offsetSymbol=='-': result = -1
    if offsetSymbol=='+': result = +1
    return result

def initSnakeLR(x,y):
    global snake
    snake = []
    for i in range(4,0,-1): # Go right to left so the rightmost is head.
        j = i*3
        code = horzSeq[j:j+3]
        snake.append( (x, y, code) ) # x,y is virtual head. Sprites might be drawn at an offset
        x -= 1

def initSnakeRL(x,y):
    global snake
    snake = []
    for i in range(4): # Go Left to Right so the leftmost is head.
        j = i*3
        code = horzSeq[j:j+3]
        snake.append( (x, y, code) ) # x,y is virtual head. Sprites might be drawn at an offset
        x += 1

def initSnakeUp(x,y):
    global snake
    snake = []
    for i in range(4,0,-1): # Go Downward so the bottom most is head.
        j = i*3
        code = vertSeq[j:j+3]
        snake.append( (x, y, code) ) # x,y is virtual head. Sprites might be drawn at an offset
        y -= 1

def initSnakeDown(x,y):
    global snake
    snake = []
    for i in range(4): # Go upward so the topmost is head.
        j = i*3
        code = vertSeq[j:j+3]
        snake.append( (x, y, code) ) # x,y is virtual head. Sprites might be drawn at an offset
        y += 1



def plotSeg(x,y, segCode, isDraw): # segCode is like d--, x,y is virtual position before offsets
    print("plotting", segCode, "at", x,y)
    spriteName = segCode[0] # grab the sprite name (ie d)
    sprite = toSprite(spriteName)
    x += toOffset(segCode[1])
    y += toOffset(segCode[2])
    plot( x, y, sprite, isDraw )

def drawSeg(x,y, segCode):
    plotSeg(x,y, segCode, True)

def eraseSeg(x,y, segCode):
    plotSeg(x,y, segCode, False)

def drawSnake():
    for s in snake:
        # each s is virtual x,y position followed by the segCode
        drawSeg(s[0], s[1], s[2])
        oled.show()

def ChopTail():
    global snake
    #-- Remove tail --
    tailIndex = len(snake)-1
    tail = snake[tailIndex] # d--, x, y
    eraseSeg(tail[0],tail[1], tail[2])
    snake.pop(tailIndex)
    
def moveSnake(dx,dy):
    global snake
    
    if dx!=0: seq = horzSeq
    if dy!=0: seq = vertSeq
    
    #-- New Head --
    curHead = snake[0]
    curHeadCode = curHead[2]
    nuX = curHead[0] + dx
    nuY = curHead[1] + dy
    if dx==1 or dy==1:
        pos = seq.find(curHeadCode)
        nuHeadCode = seq[pos+3:pos+6]
    if dx==-1 or dy==-1:
        pos = seq.rfind(curHeadCode)
        #print("found curHeadCode", curHeadCode, "at", pos, "of", seq)
        nuHeadCode = seq[pos-3:pos]
        
    nuHead = (nuX, nuY, nuHeadCode)
    print("curHead", curHead, " --> nuHeadCode", nuHeadCode)

    #-- Append New Head --
    snake.insert(0, nuHead)
    drawSeg(nuX, nuY, nuHeadCode)

    ChopTail()
    oled.show()

def UpDownLeftRightTests():
    #=== UP test ==
    oled.fill(0)
    x=int(128/3/scale/2) 
    y=0
    initSnakeUp(x,y)
    drawSnake()
    for r in range(64/3/scale):
        moveSnake(0,+1)
        sleep(spd)

    #=== DOWN test ==
    oled.fill(0)
    x=int(128/3/scale/2)
    y=int(64/3/scale)
    initSnakeDown(x,y)
    drawSnake()
    for r in range(64/3/scale):
        moveSnake(0,-1)
        sleep(spd)
        
    #=== LEFT to RIGHT test ==
    oled.fill(0)
    x=0
    y=int(64/3/scale/2)
    initSnakeLR(x,y)
    drawSnake()
    for r in range(128/3/scale):
        moveSnake(+1,0)
        sleep(spd)
        
    #=== RIGHT to LEFT test ==
    oled.fill(0)
    x=int(128/3/scale) 
    initSnakeRL(x,y)
    drawSnake()
    for r in range(128/3/scale):
        moveSnake(-1,0)
        sleep(spd)
    
def setupUI():
    global buttonRight, buttonLeft, buttonUp, buttonDown

    buttonRight = Pin(13, Pin.IN, Pin.PULL_UP)
    buttonLeft = Pin(14, Pin.IN, Pin.PULL_UP)
    buttonUp = Pin(15, Pin.IN, Pin.PULL_UP)
    buttonDown = Pin(12, Pin.IN, Pin.PULL_UP)    

def goRight():
    global snake, dx, dy
    head = snake[0]
    dx,dy=1,0
    nuX, nuY = head[0]+dx, head[1]+dy
    nuHeadCode="d--"
    snake.insert(0, (nuX,nuY,nuHeadCode))
    ChopTail()

def goLeft():
    global snake, dx, dy
    head = snake[0]
    dx,dy=-1,0
    nuX, nuY = head[0]+dx, head[1]+dy
    nuHeadCode="d--"
    snake.insert(0, (nuX,nuY,nuHeadCode))
    ChopTail()

def goUp():
    global snake, dx, dy
    head = snake[0]
    dx,dy=0,1
    nuX, nuY = head[0]+dx, head[1]+dy
    nuHeadCode="b=-"
    snake.insert(0, (nuX,nuY,nuHeadCode))
    ChopTail()

def goDown():
    global snake, dx, dy
    head = snake[0]
    dx,dy=0,-1
    nuX, nuY = head[0]+dx, head[1]+dy
    nuHeadCode="b=-"
    snake.insert(0, (nuX,nuY,nuHeadCode))
    ChopTail()

def CheckButtons():
    if buttonLeft.value()==False: goLeft()
    if buttonRight.value()==False: goRight()
    if buttonUp.value()==False: goUp()
    if buttonDown.value()==False: goDown()       
        
def main():
    sleep(1)
    i2c=I2C(1,sda=Pin(2), scl=Pin(3), freq=400000)
    global oled
    oled = SSD1306_I2C(128, 64, i2c)
    
    setupUI()

    #UpDownLeftRightTests()
    
    oled.fill(0)
    x=0
    y=int(64/3/scale/2)
    initSnakeLR(x,y)
    global dx, dy
    dx,dy=1,0
    
# horzSeq = "d--b--a-=c-=d--" #Left to Right (positive direction curve down first)
# vertSeq = "b=-c=-d--a--b=-" #Bottom to top (positive direction curve right first)

#     drawSeg(5,3,"b--")
#     #drawSeg(6,3,"a-=") # continue right
#     #drawSeg(5,2,"b=-")
#     #drawSeg(5,2,"c=-")
#     #drawSeg(5,2,"d--")
#     drawSeg(5,2,"a--")
#     oled.show()
    
    while True:
        CheckButtons()
        moveSnake(dx,dy)
        sleep(spd)
