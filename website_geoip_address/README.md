Website GeoIP Address
=====================

* Show different company's addresses based on the location of the user

In order this module to work: If your server is behind a proxy like Nginx, Gunicorn the REMOTE_ADDR 
variable becomes worthless since every connection looks like it's coming from your proxy server 
instead of the actual user making the request.
To avoid that behaviour:
1. If you're running a standalone Odoo server: start server with **--proxy-mode** command line option.
2. If you're running Odoo server over a wsgi server: add **conf['proxy_mode'] = True** to odoo-wsgi.py config file.

More info: https://github.com/odoo/odoo/issues/11035
