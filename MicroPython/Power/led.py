
from machine import Pin

_led = Pin("LED", Pin.OUT)

def update(val):
    if val == 0:
        _led.off()
    else:
        _led.on()

if __name__=='__main__':
    import time
    update(1)
    time.sleep_ms(2000)
    update(0)
    