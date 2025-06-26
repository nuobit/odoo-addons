# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

{
    "name": "Connector Extension",
    "summary": "This module extends the connector module",
    "version": "17.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "LGPL-3",
    "category": "Connector",
    "website": "https://github.com/NuoBiT/odoo-addons",
    "depends": ["connector"],
    # The dependency on queue_context is necessary so that
    # when a job calls another job, the company is not lost
}
