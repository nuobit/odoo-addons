# -*- coding: utf-8 -*-
#/#############################################################################
#
#   Odoo, Open Source Management Solution
#   Copyright (C) 2015 NuoBiT Solutions, S.L. (<http://www.nuobit.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#/#############################################################################

{
    'name': "Website GeoIP Address",
    'description': """Show different company's addresses based on the location of the user

In order this module to work: If your server is behind a proxy like Nginx, Gunicorn the REMOTE_ADDR variable becomes worthless since every connection looks like it's coming from your proxy server
instead of the actual user making the request.
To avoid that behaviour:
1. If you're running a standalone Odoo server: start server with **--proxy-mode** command line option.
2. If you're running Odoo server over a wsgi server: add **conf['proxy_mode'] = True** to odoo-wsgi.py config file.

More info: https://github.com/odoo/odoo/issues/11035

    """,
    'version': '0.0.1',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Custom',
    'website': 'https://www.nuobit.com',
    'depends': ['website'],
    'data': [
        'views/inherit_views.xml',
        'views/templates.xml'
        ],
    'installable': True,
}
