
test = 1

import Pico_LCD_114_V2

_lcd = Pico_LCD_114_V2.LCD_114(width=134)

def _display(pos, label, msg, errorlevel=0):
    pos = (pos % 6) * 2
    w = 220
    h = 14
    x = 14
    y = 14 + pos * (h + 1)
    fg = _lcd.green
    bg = _lcd.black
    if errorlevel > 0:
        fg = _lcd.yellow
    if errorlevel > 1:
        fg = _lcd.red
    _lcd.rect(x, y, w, 2*(h+1), bg, True)
    _lcd.text(label, x, y, fg)
    y = y + h
    _lcd.text(msg, x, y, fg)
    _lcd.show()

def update(config, values):
    for device in values:
        name = config[device]
        pos  = int(config[name+".POS"])
        tmp  = values[device]["TMP"]
        hum  = values[device]["HUM"]
        bat  = values[device]["BAT"]
        rssi = values[device]["RSSI"]
        if rssi < -90:
            rssi = -90
        if rssi != 0:
            rssi= int((100 + rssi)/10.0 + 0.5)
        msg = "{:.1f} {:.1f} {:.1f} {:d}".format(tmp, hum, bat, rssi)
        _display(pos, name, msg, 0 if rssi != 0 else 2)
        if test:
            print(device, name, values[device])
