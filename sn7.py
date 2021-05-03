# sn7 is the tool to help figure out which sprite should be used upon various turns.

from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
from utime import sleep, ticks_ms

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

lrSeq = "c-=a-=b--d--c-=" #Left to Right (positive direction curve down first)
rlSeq = "d=-b=-a==c==d=-" #Left to Right (NEGATIVE direction curve down first)
duSeq = "c=-b=-a--d--c=-" #Bottom to top (positive direction curve left first)
udSeq = "d-=a-=b==c==d-=" #Bottom to top (NEGATIVE direction curve left first)


snake = []
scale = 2
spd = .2 #0.05
segFrom, segTo = "c", "d"
timeToBlink, timeToBlink2 = 0,0
isOn,isOn2 = True,True
prevFrom, prevTo = -1,-1
needRefresh = True
nuDx=0
nuDy=0

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
    global snake, dx, dy
    dx,dy=+1,0
    snake = []

    for i in range(4): # Go backward so the rightmost is head.
        j = i*3
        code = lrSeq[j:j+3]
        snake.append( (x, y, code) ) # x,y is virtual head. Sprites might be drawn at an offset
        x -= 1
    
def initSnakeRL(x,y):
    global snake, dx, dy
    dx,dy=-1,0
    snake = []
    for i in range(4): # Go backward so the leftmost is head.
        j = i*3
        code = rlSeq[j:j+3]
        snake.append( (x, y, code) ) # x,y is virtual head. Sprites might be drawn at an offset
        x += 1

def initSnakeUp(x,y):
    global snake, dx, dy
    dx,dy=0,+1
    snake = []
    for i in range(4): # Go Downward so the bottom most is head.
        j = i*3
        code = duSeq[j:j+3]
        snake.append( (x, y, code) ) # x,y is virtual head. Sprites might be drawn at an offset
        y -= 1

def initSnakeDown(x,y):
    global snake, dx, dy
    dx,dy=0,-1
    snake = []
    for i in range(4): # Go upward so the topmost is head.
        j = i*3
        code = udSeq[j:j+3]
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
    
    if dx==1: seq = lrSeq
    if dx==-1: seq = rlSeq
    if dy==1: seq = duSeq
    if dy==-1: seq = udSeq
    
    #-- New Head --
    curHead = snake[0]
    curHeadCode = curHead[2]
    curSeg = curHeadCode[0]
    nuX = curHead[0] + dx
    nuY = curHead[1] + dy
    pos = seq.rfind(curSeg) # seq is listed head to tail, so to find new head we need to go backward in the seq.
    nuHeadCode = seq[pos-3:pos]
        
    nuHead = (nuX, nuY, nuHeadCode)
    print("curHead", curHead, " --> nuHeadCode", nuHeadCode)

    #-- Append New Head --
    snake.insert(0, nuHead)
    drawSeg(nuX, nuY, nuHeadCode)

    ChopTail()
    oled.show()

    
def setupUI():
    global mPotTo, mPotFrom, mZoomPot
    global buttonRight, buttonLeft, buttonUp, buttonDown

    buttonRight = Pin(13, Pin.IN, Pin.PULL_UP)
    buttonLeft = Pin(14, Pin.IN, Pin.PULL_UP)
    buttonUp = Pin(15, Pin.IN, Pin.PULL_UP)
    buttonDown = Pin(12, Pin.IN, Pin.PULL_UP)    

    mPotTo = ADC(26)
    mPotFrom = ADC(27)
    mZoomPot = ADC(28)
    
def _map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def dirToDeltas(dir):
    results = (0,0)
    if dir==0: results = (0,+1)
    if dir==1: results = (+1,0)
    if dir==2: results = (0,-1)
    if dir==3: results = (-1,0)
    return results


def dirToEnglish(dir):
    if dir==0: english = "Up"
    if dir==1: english = "Right"
    if dir==2: english = "Down"
    if dir==3: english = "Left"
    return english

def nextSeg(segName):
    if segName=="a": nextSeg="b"
    if segName=="b": nextSeg="c"
    if segName=="c": nextSeg="d"
    if segName=="d": nextSeg="a"
    sleep(.5)
    return nextSeg

def prevSeg(segName):
    if segName=="a": nextSeg="d"
    if segName=="b": nextSeg="a"
    if segName=="c": nextSeg="b"
    if segName=="d": nextSeg="c"
    sleep(.5)
    return prevSeg

def segNameToSnake(segHead, dir, headX, headY, lookForward):
    codes = []
    if dir == 0: seq = duSeq
    if dir == 1: seq = lrSeq
    if dir == 2: seq = udSeq
    if dir == 3: seq = rlSeq
    if lookForward:
        pos = seq.find(segHead)
        c1 = seq[pos:pos+3]
        codes.append(c1)
        
        pos = seq.find(c1) # seq is listed head to tail, so to find new head we need to go backward in the seq.
        c2 = seq[pos+3:pos+6]
        codes.append(c2)
        
        pos = seq.find(c2) # seq is listed head to tail, so to find new head we need to go backward in the seq.
        c3 = seq[pos+3:pos+6]
        codes.append(c3)
        
        pos = seq.find(c3) # seq is listed head to tail, so to find new head we need to go backward in the seq.
        c4 = seq[pos+3:pos+6]
        codes.append(c4)
    else:
        pos = seq.find(segHead) # first one you always find forward
        c1 = seq[pos:pos+3]
        codes.append(c1)
    
        pos = seq.rfind(c1) # seq is listed head to tail, so to find new head we need to go backward in the seq.
        c2 = seq[pos-3:pos]
        codes.append(c2)
        
        pos = seq.rfind(c2) # seq is listed head to tail, so to find new head we need to go backward in the seq.
        c3 = seq[pos-3:pos]
        codes.append(c3)
        
        pos = seq.rfind(c3) # seq is listed head to tail, so to find new head we need to go backward in the seq.
        c4 = seq[pos-3:pos]
        codes.append(c4)

    dx,dy = dirToDeltas(dir)
         
    x,y = headX, headY
    snake = []
    for code in codes:
        snake.append( (x,y, code) ) # x,y is virtual head. Sprites might be drawn at an offset
        if lookForward:
            x -= dx # minus because we'd adding segs head to tail, so coords are backward
            y -= dy
        else:
            x += dx
            y += dy

    return snake

def CheckButtons():
    global dx,dy, nuDx, nuDy, segFrom, segTo
    global prevFrom, prevTo, needRefresh
    dFrom = int(_map( mPotFrom.read_u16(), 0,65025, 0,3))
    dTo =  int(_map( mPotTo.read_u16(), 0,65025, 0,3))
    
    if dFrom != prevFrom or dTo != prevTo:
        needRefresh=True
     
    dx,dy = dirToDeltas(dFrom)
    nuDx, nuDy = dirToDeltas(dTo)

    if buttonLeft.value()==False:
        segFrom=nextSeg(segFrom)
        needRefresh=True
    if buttonRight.value()==False:
        segTo=nextSeg(segTo)
        needRefresh=True

    if needRefresh:
        oled.fill(0)
        oled.text(dirToEnglish(dFrom), 0,0)
        oled.text(dirToEnglish(dTo), 60,0)  
        oled.text(segFrom.upper(), 0+24,10)
        oled.text(segTo.upper(), 60+24,10)
    
        global snake
        snake = segNameToSnake(segFrom, dFrom, snakeX, snakeY, True)
        drawSnake()
        
        snake = segNameToSnake(segTo, dTo, snakeX+nuDx, snakeY+nuDy, False)
        drawSnake()
        
        prevFrom, prevTo = dFrom, dTo
        needRefresh=False

        oled.show()

def BlinkFromOrigin():
    global isOn, snakeX, snakeY, timeToBlink
    x,y = snakeX, snakeY
    if ticks_ms() >= timeToBlink:   
        oled.rect(x*3*scale+0*scale,63-y*3*scale-0*scale, scale,scale, 1 if isOn else 0)
        isOn = not isOn
        timeToBlink = ticks_ms() + 600
        oled.show()

def BlinkToOrigin():
    global isOn2, snakeX, snakeY, nuDx, nuDy, timeToBlink2
    x,y = snakeX+nuDx, snakeY+nuDy
    if ticks_ms() >= timeToBlink2:   
        oled.rect(x*3*scale+0*scale,63-y*3*scale-0*scale, scale,scale, 1 if isOn2 else 0)
        isOn2 = not isOn2
        timeToBlink2 = ticks_ms() + 200
        oled.show()

def main():
    sleep(1)
    i2c=I2C(1,sda=Pin(2), scl=Pin(3), freq=400000)
    global oled
    oled = SSD1306_I2C(128, 64, i2c)
    
    setupUI()
    
    oled.fill(0)
    x=int(128/3/scale/2)
    y=int(64/3/scale/2)
    global snakeX, snakeY 
    snakeX, snakeY = int(128/3/scale/2), int(64/3/scale/2)
      
    #initSnakeRL(x,y)
    initSnakeLR(x,y)
    #initSnakeUp(x,y)
    #initSnakeDown(x,y)
    
    while True:
        CheckButtons()
        BlinkFromOrigin()
        BlinkToOrigin()
        #moveSnake(dx,dy)
        #sleep(spd)
        #moveSnake(dx,dy)
        #sleep(spd)
