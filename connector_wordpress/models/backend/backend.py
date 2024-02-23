# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WordPressBackend(models.Model):
    _name = "wordpress.backend"
    _inherit = "connector.extension.backend"
    _description = "WordPress Backend"

    name = fields.Char(
        required=True,
    )
    url = fields.Char(
        help="WordPress URL",
        required=True,
    )
    consumer_key = fields.Char(
        help="WordPress Consumer Key",
        required=True,
    )
    consumer_secret = fields.Char(
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
        ondelete="restrict",
    )
    verify_ssl = fields.Boolean(
        default=True,
        help="Verify SSL certificate of the WordPress server.",
    )
    test_database = fields.Boolean(
        default=False,
        help="If a test database is being used, the attachments routes can be empty."
        "This check allow to avoid the error of not "
        "finding the image and don't raise an error.",
    )
