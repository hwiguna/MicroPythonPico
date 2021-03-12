def main():
    import machine
    import utime
    
    pot0 = machine.ADC(26)
    pot1 = machine.ADC(27)
    pot2 = machine.ADC(28)
    
    while True:
        print(pot0.read_u16(), pot1.read_u16(), pot2.read_u16())
        utime.sleep(.5)