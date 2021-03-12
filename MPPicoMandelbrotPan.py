from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
import framebuf
import time
import mandelbrot

#-- Parameters --
WIDTH, HEIGHT = 128, 64
width2 = int(WIDTH/2)
height2 = int(HEIGHT/2)

realStart, realEnd = -2-.8, 2
imStart, imEnd = -1,1

def DrawMandelbrot():
    global oled, brotFB, cursorFB
    print("DRAWING:",realStart, realEnd, imStart, imEnd)
    RE_START = realStart
    RE_END = realEnd
    IM_START = imStart
    IM_END = imEnd

    MAX_ITER = 80
    brotFB.fill(0)
    for x in range(0, WIDTH):
        xx = RE_START + (x / WIDTH) * (RE_END - RE_START)
        for y in range(0, HEIGHT):
            yy = IM_START + (y / HEIGHT) * (IM_END - IM_START)
            c = complex(xx, yy) # Convert pixel coordinate to complex number
            m = mandelbrot.mandelbrot(c)   # Compute the number of iterations
            color = 1 - int(m/MAX_ITER)
            brotFB.pixel(x,y, 1 if color>0 else 0) # Plot the point
        if x % 4 == 0:
            oled.blit(brotFB,0,0)
            oled.show()
    oled.show()


def SetupDisplay():
    global oled
    i2c=I2C(1,sda=Pin(2), scl=Pin(3), freq=400000)
    oled = SSD1306_I2C(128, 64, i2c)
    
def SetupFB():
    global brotBitmap, brotFB, cursorFB

    #-- Mandelbrot canvas --
    brotBitmap=bytearray(int(WIDTH*HEIGHT/8))
    brotFB=framebuf.FrameBuffer(brotBitmap, WIDTH,HEIGHT, framebuf.MVLSB)
    
    #-- Cursor --
    cursorBitmap=bytearray(int(WIDTH*HEIGHT/8))
    cursorFB = framebuf.FrameBuffer(cursorBitmap, WIDTH,HEIGHT, framebuf.MVLSB)
    cursorFB.line(0,0, WIDTH, HEIGHT, 1)  

def SetupUI():
    global mPot0, mPot1, mZoomPot
    global buttonZoomIn, buttonZoomOut, buttonCenter
    
    #-- Setup UI --
    mPot0 = ADC(26)
    mPot1 = ADC(27)
    mZoomPot = ADC(28)
    
    buttonZoomIn = Pin(13, Pin.IN, Pin.PULL_UP)
    buttonZoomOut = Pin(14, Pin.IN, Pin.PULL_UP)
    buttonCenter = Pin(15, Pin.IN, Pin.PULL_UP)

def Setup():
    global oled, brotFB, cursorFB
    SetupDisplay()
    SetupFB()
    SetupUI()

def get_pixel(buffer, x,y):
    yy = y % 8
    return 1 if (buffer[x+WIDTH*int(y/8)] & (1<<yy)) > 0 else 0
    
def _map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def getCursorX(pot):
    return int(_map(pot.read_u16(), 0, 65520, -WIDTH, WIDTH))

def getCursorY(pot):
    return int(_map(pot.read_u16(),0, 65520, -HEIGHT, HEIGHT))

def getZoomLevel(pot):
    return int(_map(pot.read_u16(), 0, 65520, 0, HEIGHT))

def MockDraw(x0, y0, zoomLevel):
    global brotBitmap
    if zoomLevel == 1:
        oled.blit(brotFB, x0, y0)
        oled.show()
    elif zoomLevel == 2:
        for x in range(0, WIDTH, 2):
            for y in range(0, HEIGHT, 2):
                c = get_pixel(brotBitmap, x, y)
                oled.fill_rect(x,y,2,2,c)
                oled.show()
    
def Loop():
    global mPot0, mPot1, mZoomPot
    global oled, brotFB, cursorFB
    global buttonZoomIn, buttonZoomOut, buttonCenter

    DrawMandelbrot() # Draw initial Mandelbrot
    nextSensorRead=-1
    lastX0, lastY0 = -1024,-1024
    zoomLevel = 1
    while True:
        if time.ticks_ms() >= nextSensorRead:          
            xd = getCursorX(mPot0)
            yd = getCursorY(mPot1)
            zd = getZoomLevel(mZoomPot)
            
            x0 = xd
            y0 = yd
            
            if abs(x0-lastX0)>1 or abs(y0-lastY0)>1:
                lastX0, lastY0 = x0, y0
                oled.fill(0)
                print("DRAW at zoomLevel=", zoomLevel)
                MockDraw(x0, y0, zoomLevel)
                
            if buttonZoomIn.value()==0:
                zoomLevel+=1
                print("zoomLevel=", zoomLevel)
            
            if buttonZoomOut.value()==0:
                zoomLevel-=1
                print("zoomLevel=", zoomLevel)

#display.framebuffer(cursor, 0,0)
            nextSensorRead = time.ticks_ms() + 100

def main():
    Setup()
    Loop()

#     b2=bytearray(40)
#     b2[0]=255
#     b2[1]=0
#     b2[2]=0
#     b2[3]=255
#     fb = framebuf.FrameBuffer(b2, 5,8, framebuf.MVLSB)
#     oled.blit(fb,20,0)
#     oled.show()