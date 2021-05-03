from machine import Pin, I2C, 
from ssd1306 import SSD1306_I2C
import math
from utime import ticks_ms,sleep
import gc

WIDTH, HEIGHT = 128, 64
x0, y0 = int(WIDTH/2), int(HEIGHT/2)
BUS,SDA,SCL = 1, 2,3

charWidth, charHeight, charSlant = 20,30,3 # 10,15,2 # 
cw,ch,cs = int(charWidth/2), int(charHeight/2), charSlant
spacing = charWidth+3*cs
nodes = [(0,0),(cs,ch),(cs+cs,charHeight),(cs+cs+cw,charHeight),(cs+cs+charWidth,charHeight),(charWidth+cs,ch),(charWidth,0),(cw,0),(cw+cs,ch)]
segs = {} # Dictionary of segments. Key is the name of the segment. Value is a tuple of 4 integers (x,y x,y)
chars = {} # Dictionary for ascii chars. Key is the ascii char. Value is a string containing all the segments for that char.

testSpeed=.2

def setupOled():
    global oled
    i2c = I2C(BUS, sda=Pin(SDA), scl=Pin(SCL), freq=400000)
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
    oled.fill(0)

def makeSeg(key, i,j):
    global nodes, segs
    segs[key]=(nodes[i][0],HEIGHT-1-nodes[i][1], nodes[j][0],HEIGHT-1-nodes[j][1]) # Each dictionary content is a tuple of four numbers

def setupSegs():
    global nodes,segs
    makeSeg("a", 0,1)
    makeSeg("b", 1,2)
    makeSeg("c", 2,4)
    makeSeg("d", 4,5)
    makeSeg("e", 5,6)
    makeSeg("f", 6,0)
    makeSeg("g", 8,1)
    makeSeg("h", 8,2)
    makeSeg("i", 8,3)
    makeSeg("j", 8,4)
    makeSeg("k", 8,5)
    makeSeg("l", 8,6)
    makeSeg("m", 8,7)
    makeSeg("n", 8,0)

def setupChars():
    global chars
    chars[" "]=""
    chars["'"]="i"
    chars["*"]="ghijklmn"
    chars["+"]="gikm"
    chars["-"]="gk"
    chars["/"]="jn"
    chars["0"]="abcdefjn"
    chars["1"]="fim"
    chars["2"]="cjgaf"
    chars["3"]="cjkef"
    chars["4"]="bgkde"
    chars["5"]="cbglf"
    chars["6"]="abcefgk"
    chars["7"]="cjn"
    chars["8"]="abcdefgk"
    chars["9"]="bcdfgk"
    chars["A"]="abcdegk"
    chars["B"]="cdefikm"
    chars["C"]="abcf"
    chars["D"]="cdefim"
    chars["E"]="abcfg"
    chars["F"]="abcg"
    chars["G"]="abcefk"
    chars["H"]="abdegk"
    chars["J"]="adef"
    chars["I"]="cfim"
    chars["K"]="abgjl"
    chars["L"]="abf"
    chars["M"]="abhjde"
    chars["N"]="abhlde"
    chars["O"]="abcdef"
    chars["P"]="abcdgk"
    chars["Q"]="abcdefl"
    chars["R"]="abcdgkl"
    chars["S"]="bcefgk"
    chars["T"]="cim"
    chars["U"]="abedf"
    chars["V"]="abjn"
    chars["W"]="abdeln"
    chars["X"]="hjln"
    chars["Y"]="hjm"
    chars["Z"]="cjnf"

def drawSeg(segName, x=0, y=0):
    s = segs[segName]
    oled.line(x+s[0],y+s[1],x+s[2],y+s[3], 1)

def drawChar(char, x=0, y=0):
    global chars
    segments = chars[char]
    for s in range(len(segments)):
        drawSeg(segments[s], x,y)

def drawWord(str):
    oled.fill(0)
    for c in range(len(str)):
        drawChar(str[c], x=c*spacing, y=0)
        oled.show()
        sleep(.1)

def testIndividualSegs():
    for i in range(14):
        oled.fill(0)
        drawSeg(chr( ord('a') + i))
        oled.show()
        sleep(testSpeed)

def rotationAnim():
    anim="ghijklmn"
    frame="abcdef"
    for r in range(3):
        for a in range(len(anim)):
            oled.fill(0)
            # Draw Frame
            for f in range(len(frame)):
                drawSeg(frame[f])
            
            drawSeg(anim[a])
            oled.show()
            sleep(testSpeed)

def testChar(char):
    oled.fill(0)
    drawChar(char)
    oled.show()
    sleep(testSpeed)
    
def testChars():
    testChar("'")
    testChar(" ")
    testChar("*")
    testChar("+")
    testChar("-")
    testChar("/")
    for a in range(ord('A'), ord('Z')+1):
        oled.fill(0)
        drawChar(chr(a))
        oled.show()
        sleep(testSpeed)

def main():
    setupOled()
    setupSegs()
    setupChars()
    testIndividualSegs()
    rotationAnim()  
    testChars()
    drawWord("HARI")
    print(gc.mem_free())
