# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _

BATCH_SENDING_METHODS = [
    ('pdf', _('PDF')),
    ('email', _('e-mail')),
    ('signedfacturae', _('Factura-e signed')),
    ('unsignedfacturae', _('Factura-e unsigned')),
]
