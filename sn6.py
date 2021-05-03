from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from utime import sleep

# Terminologies:
# Everything is made up of four arc sprites: a,b,c,d.
# Sequence defines the order of arcs to create the slithering "S" curve.
# each arc is followed by two characters that indicate where origin where the arc should be drawn at relative to the snake position.
# These three characters are collectively called a "code"

# turntable is a very tedious lookup dictionary.
# key is the current arc and its current and desired turning direction
# value is what segment should be drawn to accomplish that turning.

# snake is an array of segments. Each segment contains x,y,Code.
# x,y is actual snake segment position.
# Code is the arc (sprite) and the two character code specifycing where the origin of the sprite should be drawn.

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

turnTable = {
    "d+==+": (0,0, "b=-"), #d right to up 
    "d+==-": (0,-1,"c=-"), #d right to down
    "b+==+": (0,1, "b--"), #b right to up
    "b+==-": (0,-1,"c=-"), #b right to down
    "c+==+": (0,-1,"c=="), #c right to up
    "c+==-": (0,1, "b=-"), #c right to down
    "a+==+": (0,0, "c=="), #a right to up
    "a+==-": (0,1, "b=-"), #a right to down

    "d-==+": "b..", #d left to up
    "d-==-": "c..", #d left to down
    "b-==+": "b..", #b left to up
    "b-==-": "c..", #b left to down
    "c-==+": "b..", #c left to up
    "c-==-": "a..", #c left to down
    "a-==+": "b..", #a left to up
    "a-==-": "c..", #a left to down
    
    "d=++=": "b..", #d up to right
    "d=+-=": "c..", #d up to left
    "a=++=": "b..", #a up to right
    "a=+-=": "c..", #a up to left
    "b=++=": "b..", #b up to right
    "b=+-=": "a..", #b up to left
    "c=++=": "b..", #c up to right
    "c=+-=": "c..", #c up to left
    
    "d=-+=": "b..", #d down to right
    "d=--=": "c..", #d down to left
    "a=-+=": "b..", #a down to right
    "a=--=": "c..", #a down to left
    "b=-+=": "b..", #b down to right
    "b=--=": "a..", #b down to left
    "c=-+=": "b..", #c down to right
    "c=--=": "c..", #c down to left
}

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

def fromOffset(dx,dy):
    sym = "-=+"
    return sym[dx+1] + sym[dy+1]

def initSnakeLR(x,y):
    global snake
    snake = []
    for i in range(3,0,-1): # Go right to left so the rightmost is head.
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
    curSeg = curHeadCode[0]
    nuX = curHead[0] + dx
    nuY = curHead[1] + dy
    if dx==1 or dy==1:
        pos = seq.find(curSeg)
        nuHeadCode = seq[pos+3:pos+6]
    if dx==-1 or dy==-1:
        pos = seq.rfind(curSeg)
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

def RightToUp(seg):
    x,y,code=seg[0],seg[1],seg[2]
    if code[0]=="d": nuX,nuY,nuHeadCode=x+0,y+0,"b=-"
    if code[0]=="b": nuX,nuY,nuHeadCode=x+0,y+1,"c=-"
    if code[0]=="a": nuX,nuY,nuHeadCode=x+0,y+1,"b=-"
    if code[0]=="c": nuX,nuY,nuHeadCode=x+0,y+1,"b=-"
    return (nuX,nuY,nuHeadCode)

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
    nuDx, nuDy = 0,1
    headSeg = snake[0]
    headSpriteName = headSeg[2][0]
    print("goUp. headSeg", headSeg, "headSpriteName", headSpriteName)
    if headSpriteName == "b":
        key = headSpriteName + fromOffset(dx,dy) + fromOffset(nuDx, nuDy)
        print("goUp. headSeg", headSeg, "key", key)

        nuHeadSeg = turnTable[key]
        print("goUp. nuHeadSeg", nuHeadSeg)
        hx,hy=nuHeadSeg[0], nuHeadSeg[1]
        nuX, nuY, nuHeadCode = headSeg[0]+hx, headSeg[1]+hy, nuHeadSeg[2]
        print("goUp. nuX,nuY,nuHeadSeg", nuX,nuY,nuHeadSeg)
        snake.insert(0, (nuX,nuY,nuHeadCode))
        ChopTail()
        dx,dy=nuDx,nuDy
        exit

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
    #if buttonUp.value()==False:
    goUp()
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
    #drawSnake()
    
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
        moveSnake(dx,dy)
        sleep(spd)
