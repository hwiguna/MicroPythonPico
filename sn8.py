# sn8 uses the new turntable.

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

snake = []
scale = 1
spd = .2 #0.05

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

turnTable = {
# Left to right
"a+==+": "a", # a smooth, c backtracks
"a+==-": "d", # was d, b continues but with gap, d backtracks but no gap.
"b+==+": "d", # d tight, alternatively b if larger radius desired.
"b+==-": "c", # a loops, c is tight turn
"c+==+": "b", # b is tight turn
"c+==-": "a", # a is tight turn
"d+==+": "c", # c is continuing curve but with gap, a backtracks
"d+==-": "d", # d is larger arc, b backtracks

# Right to left
"a-==+": "d", # d tight, b loops
"a-==-": "c", # c tight, a larger arc
"b-==+": "a", # a continues but gap, c backtracks
"b-==-": "b", # d backtracks, b larger arc
"c-==+": "c", # a backtracks, c larger arc
"c-==-": "d", # b backtracks, d continues with gap
"d-==+": "a", # a tight, c larger arc
"d-==-": "a", # a tight turn, c bad coil

# Up
"a=++=": "d", # d tight, a big arc
"a=+-=": "c", # b loops, c tight
"b=++=": "b", # b big arc, c backtracks
"b=+-=": "a", # d backtracks, a continue with break
"c=++=": "a", # a tight, d loops
"c=+-=": "b", # c big arc, b tight
"d=++=": "c", # c continue with break, b backtracks
"d=+-=": "d", # d big arc, a backtracks

# Down
"a=-+=": "c", # b continue with gap, c backtracks
"a=--=": "d", # a big arc, d backtracks
"b=-+=": "d", # d tight, a loops
"b=--=": "c", # b big arc, c tight
"c=-+=": "b", # b backtracks, c big loop
"c=--=": "d", # d continue with gap, a backtracks
"d=-+=": "a", # d big arc, a tight
"d=--=": "b" # b tight, c loops
}


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

def deltaToSeq(dx,dy):
    if dx==1: seq = lrSeq
    if dx==-1: seq = rlSeq
    if dy==1: seq = duSeq
    if dy==-1: seq = udSeq
    return seq
    
def toCode(spriteName, dx,dy):
    seq = deltaToSeq(dx,dy)
    pos = seq.find(spriteName)
    return seq[pos:pos+3]
    
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
    
    seq = deltaToSeq(dx,dy)
    print("MoveSnake. dx,dy", dx, dy)
    
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
    

def changeDir(nuDx, nuDy):
    global snake, dx, dy
    
    if dx==nuDx and dy==nuDy:
        return
    
    print("changeDir. BEGIN from", dx, dy, "to", nuDx, nuDy)

    headSeg = snake[0] #x,y,spriteCode
    headSpriteName = headSeg[2][0] # take first char of sprite code -> sprite name
    print("changeDir. headSeg", headSeg, "headSpriteName", headSpriteName)
    key = headSpriteName + fromOffset(dx,dy) + fromOffset(nuDx, nuDy)
    print("changeDir. key", key)

    nuSpriteName = turnTable[key]
    print("changeDir. Turntable value is nuSpriteName", nuSpriteName)
    nuCode = toCode(nuSpriteName, nuDx, nuDy)
    nuX, nuY = headSeg[0]+nuDx, headSeg[1]+nuDy
    print("changeDir. nuX,nuY,nuCode", nuX,nuY,nuCode)
    snake.insert(0, (nuX,nuY,nuCode))
    drawSeg(nuX, nuY, nuCode) # new head is created due to turning, so draw this new head!
    
    ChopTail()
    dx,dy=nuDx,nuDy
    #bougs()

def _map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def dirToDeltas(dir):
    results = (0,0)
    if dir==0: results = (0,+1)
    if dir==1: results = (+1,0)
    if dir==2: results = (0,-1)
    if dir==3: results = (-1,0)
    return results

def CheckButtons():
    if buttonLeft.value()==False:  changeDir(-1,0)
    if buttonRight.value()==False:  changeDir(1,0)
    if buttonUp.value()==False: changeDir(0,1)
    if buttonDown.value()==False: changeDir(0,-1)

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
        moveSnake(dx,dy)
        sleep(spd)
        CheckButtons()
        #moveSnake(dx,dy)
        #sleep(spd)
