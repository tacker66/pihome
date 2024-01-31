
# https://github.com/tacker66/picoweb

import picoweb

from micropython import const
_html_head  = const('<html><head><title>pihome</title><meta http-equiv="refresh" content="30"><head><body><h2>pihome</h2>')
_html_tail  = const('</body></html>\n')
index_html = _html_head + _html_tail

def update(config, values):
    global index_html
    s = ""                       
    s = s + '\n<h3>APSystems EZ1</h3><table border="1">\n'
    for value in sorted(values, reverse=True):
        s = s + '<tr><td align="right">' + str(value) + '</td>\n<td align="left">' + str(values[value]) + '</td></tr>\n'
    s = s + '</table>\n'
    s = _html_head + s + _html_tail
    index_html = s
    
def indexhtml(req, resp):
    yield from resp.awrite(index_html)

ROUTES  = [("/", indexhtml), ]

def start_webserver(name):
    app = picoweb.WebApp(name, ROUTES)
    app.run()
