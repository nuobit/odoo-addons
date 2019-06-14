# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo import tools


class PayslipLineTransferBinder(Component):
    """ Bind records and give odoo/sage ids correspondence

    Binding models are models called ``sage.{normal_model}``,
    like ``sage.res.partner`` or ``sage.product.product``.
    They are ``_inherits`` of the normal models and contains
    the Sage ID, the ID of the Sage Backend and the additional
    fields belonging to the Sage instance.
    """
    _name = 'sage.payroll.sage.payslip.line.transfer.binder'
    _inherit = 'sage.binder'

    _apply_on = 'sage.payroll.sage.payslip.line.transfer'

    _external_field = ['sage_codigo_empresa', 'sage_ano', 'sage_mesd',
                       'sage_tipo_proceso',
                       'sage_codigo_empleado', 'sage_codigo_concepto_nom',
                       'sage_codigo_convenio', 'sage_fecha_registro_cv', 'sage_fecha_cobro']
