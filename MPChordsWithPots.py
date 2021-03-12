def main():
    from machine import Pin, I2C, ADC
    from ssd1306 import SSD1306_I2C
    import math

    WIDTH, HEIGHT = 128, 64
    x0, y0 = int(WIDTH/2), int(HEIGHT/2)

    def SetupOLED():
        global oled
        i2c=I2C(1,sda=Pin(2), scl=Pin(3), freq=400000)
        oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

    def SetupUI():
        global rotPot, zoomPot, nodePot
        rotPot = ADC(27)
        zoomPot = ADC(26)
        nodePot = ADC(28)

    def GetRotation():
        return  (65520 - rotPot.read_u16()) * 270 / 65520

    def GetRadius():
        return  60 #5 + int(zoomPot.read_u16() * (WIDTH*2) / 65520)

    def GetNodeCount():
        return  8 #3 + int(nodePot.read_u16() * 10 / 65520)

    def DrawChord(rotDegrees, numNodes, radius):
        r = radius
        points = []
        rot = rotDegrees*2*math.pi/360
        for i in range(numNodes):
            a = rot+ (i * math.pi * 2 / numNodes)
            points.append( (int(x0 + math.sin(a)*r), int(y0 + math.cos(a)*r)) )

        oled.fill(0)
        for i in range(numNodes-1):
            for j in range(i, numNodes):
                oled.line(points[i][0], points[i][1], points[j][0], points[j][1], True)
        oled.show()

    def DoChord():
        lastRotation, lastNumNodes, lastRadius = -1, -1,-1
        while True:
            numNodes = GetNodeCount()
            radius = GetRadius()
            newRotation = GetRotation()
            if numNodes!=lastNumNodes or abs(newRotation-lastRotation) > 4 or abs(radius-lastRadius)>2:
                DrawChord(newRotation, numNodes, radius)
                lastRotation = newRotation
                lastNumNodes = numNodes
                lastRadius = radius

    SetupOLED()
    SetupUI()
    DoChord()