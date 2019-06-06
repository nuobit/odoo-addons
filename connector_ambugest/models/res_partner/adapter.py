# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import job


class ResPartnerAdapter(Component):
    _name = 'ambugest.res.partner.adapter'
    _inherit = 'ambugest.adapter'
    _apply_on = 'ambugest.res.partner'

    _sql = """select p."EMPRESA", p."Codi UP" as "CodiUP", p."Nom UP" as "NomUP"
              from %(schema)s."Unidades productivas" p
              where p."Activa_en_AmbuGEST" = 1 and 
                    cast(p."Codi UP" as integer) >= 90000
     """
    _id = ('EMPRESA', 'CodiUP')
