# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


class ResPartnerAdapter(Component):
    _name = 'oxigesti.res.partner.adapter'
    _inherit = 'oxigesti.adapter'
    _apply_on = 'oxigesti.res.partner'

    _sql = """select c.Codigo_Mutua, c.Nombre_Mutua, c.Codigo_Cliente_Logic
              from %(schema)s.Mutuas_y_Clientes c
     """
    _id = ('Codigo_Mutua',)
