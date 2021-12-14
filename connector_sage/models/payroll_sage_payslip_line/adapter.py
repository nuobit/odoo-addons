# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import AbstractComponent


class PayslipLineAdapter(AbstractComponent):
    _name = "sage.payroll.sage.payslip.line.adapter"
    _inherit = "sage.adapter"
