
# https://github.com/tacker66/picoweb

import picoweb

from micropython import const
_html_head  = const('<html><head><title>pihome</title><meta http-equiv="refresh" content="30"><head><body><h2>pihome</h2>')
_html_tail  = const('</body></html>\n')
index_html = _html_head + _html_tail

def update(config, values):
    global index_html
    devices = dict()
    for device in values:
        s = ""                       
        name = config[device]
        s = s + '\n<h3>' + name + ' (' + device + ')' + '</h3><table border="1">\n'
        for value in sorted(values[device]):
            s = s + '<tr><td align="right">' + str(value) + '</td>\n<td align="left">' + str(values[device][value]) + '</td></tr>\n'
        s = s + '</table>\n'
        pos = config[name+".POS"]
        devices[pos] = s
    s = _html_head
    for pos in sorted(devices):
        s = s + devices[pos]
    s = s + _html_tail
    index_html = s
    
def indexhtml(req, resp):
    yield from resp.awrite(index_html)

ROUTES  = [("/", indexhtml), ]

def start_webserver(name):
    app = picoweb.WebApp(name, ROUTES)
    app.run()
