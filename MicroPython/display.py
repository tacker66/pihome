
test = 1

import Pico_LCD_114_V2

_lcd = Pico_LCD_114_V2.LCD_114(width=157)

def _display(pos, label, msg, warning=False, error=False):
    pos = (pos % 6) * 2
    w = 220
    h = 14
    x = 14
    y = 14 + pos * (h + 1)
    fg = _lcd.green
    bg = _lcd.black
    if warning:
        fg = _lcd.yellow
    if error:
        fg = _lcd.red
    _lcd.rect(x, y, w, 2*(h+1), bg, True)
    _lcd.text(label, x, y, fg)
    y = y + h
    _lcd.text(msg, x, y, fg)
    _lcd.show()

def update(config, values):
    for device in values:
        name = config[device]
        pos = int(config[name+".POS"])
        act = int(values[device]["ACT"])
        tmp = values[device]["TMP"]
        hum = values[device]["HUM"]
        bat = values[device]["BAT"]
        rssi= int((100 + values[device]["RSSI"])/10.0 + 0.5)
        err = values[device]["ERR"]
        msg = "{:.1f} {:.1f} {:.1f} {:d} {:d}".format(tmp, hum, bat, rssi, err)
        _display(pos, name, msg, False, act)
        if test:
            print(device, name, values[device])
