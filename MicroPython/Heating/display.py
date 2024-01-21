
test = 1

from Pico_LCD_114_V2 import LCD_114 as LCD

_num_pos   = 6
_start_x   = 0
_start_y   = 0
_height    = 10

def init(config):
    global _lcd, _lcd_width, _lcd_height
    _lcd_height= int(config["display_entries"]) * (_height + 1) * 2
    _lcd_width = int(config["display_width"]) + _start_y
    _lcd = LCD(width=_lcd_width, height=_lcd_height)

def _display(pos, label, msg, errorlevel=0):
    pos = (pos % _num_pos) * 2
    h = _height
    x = _start_x
    y = _start_y + pos * (h + 1)
    fg = LCD.GREEN
    bg = LCD.BLACK
    if errorlevel > 0:
        fg = LCD.YELLOW
    if errorlevel > 1:
        fg = LCD.RED
    if errorlevel > 2:
        fg = LCD.WHITE
    _lcd.rect(x, y, _lcd_width, 2*(h+1), bg, True)
    _lcd.text(label, x, y, fg)
    y = y + h
    _lcd.text(msg, x, y, fg)
    _lcd.show()

def update_border(errorlevel=0):
    if errorlevel == 0:
        _lcd.v_border_color = LCD.BLACK
    if errorlevel == 1:
        _lcd.v_border_color = LCD.YELLOW
    if errorlevel > 1:
        _lcd.v_border_color = LCD.RED

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
        dname = name+".NAM"
        if dname in config:
            name = config[dname]
        errorlevel = 0
        if rssi == 0:
            errorlevel = 2
        if tmp <= 0.0:
            errorlevel = 3
        _display(pos, name, msg, errorlevel)
        if test:
            print(device, name, values[device])
