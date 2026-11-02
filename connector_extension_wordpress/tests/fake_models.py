# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class ConnectorExtensionWordpressTestBackend(models.Model):
    """The fields the WordPress adapter reads from its backend."""

    _name = "connector.extension.wordpress.test.backend"
    _inherit = "connector.extension.backend"
    _description = "WordPress Test Backend"

    url = fields.Char(string="Site URL")
    username = fields.Char()
    application_password = fields.Char()
    verify_ssl = fields.Boolean(string="Verify SSL", default=True)


class ConnectorExtensionWordpressTestShopBackend(models.Model):
    """A shop backend that calls WordPress with the credentials of a linked
    WordPress backend, as the WooCommerce connector does."""

    _name = "connector.extension.wordpress.test.shop.backend"
    _inherit = "connector.extension.wordpress.test.backend"
    _description = "WordPress Test Shop Backend"

    wordpress_backend_id = fields.Many2one(
        comodel_name="connector.extension.wordpress.test.backend",
        string="WordPress Backend",
    )
