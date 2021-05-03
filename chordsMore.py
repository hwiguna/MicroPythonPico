from machine import Pin, I2C, 
from ssd1306 import SSD1306_I2C
import math
from utime import ticks_ms

WIDTH, HEIGHT = 128, 64
x0, y0 = int(WIDTH/2), int(HEIGHT/2)
BUS,SDA,SCL = 1, 2,3

def setupOled():
    global oled
    i2c = I2C(BUS, sda=Pin(SDA), scl=Pin(SCL), freq=400000)
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
    oled.fill(0)

def drawChord(org, chordRot, r, nodes):
    global oled
    orgx,orgy = org[0], org[1]
    p = [(int,int)] * nodes
    for i in range(nodes):
        a = math.pi*2*i/nodes
        x = orgx + math.sin(chordRot+a)*r # Sine is opposite/hypotenuse.  opposite is Y, hypotenuse is R
        y = orgy + math.cos(chordRot+a)*r
        p[i] = (int(x),int(y))
    
    for i in range(nodes-1):
        for j in range(i+1, nodes):
            pi,pj=p[i],p[j]
            oled.line(pi[0],pi[1], pj[0],pj[1], 1)
    
def drawChords():
    global oled
    
    # Origin Parameters
    orgCount = 4
    orgR = 40
    orgs = [(int,int)] * orgCount
    orgRot = 0
    orgSpeed = -math.pi/500

    # Chord Parameters
    nodes = 3
    chordR = 30
    chordRot = 0
    chordSpeed = math.pi/50
    
    timeToRotateEverything = -1
    while True:       
        if ticks_ms() > timeToRotateEverything:
            for i in range(orgCount):
                a = math.pi*2*i/orgCount
                x = x0 + math.sin(orgRot+a)*orgR # Sine is opposite/hypotenuse.  opposite is Y, hypotenuse is R
                y = y0 + math.cos(orgRot+a)*orgR
                orgs[i] = (int(x),int(y))
            
                orgRot += orgSpeed
                chordRot += chordSpeed
            timeToRotateEverything = ticks_ms() + 10
        
        # draw chords
        oled.fill(0)
        for oi in range(orgCount):
            drawChord(orgs[oi], chordRot, chordR, nodes)
        oled.show()

def main():
    setupOled()
    drawChords()    
