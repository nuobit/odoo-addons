# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PayslipProcess(models.Model):
    _name = "payroll.sage.payslip.process"
    _description = "Payslip Process"
    _order = "name"

    name = fields.Char(required=True)

    @api.constrains("name")
    def _check_name(self):
        for ppt in self:
            others = self.env[self._name].search([("id", "!=", ppt.id)])
            similar = others.filtered(
                lambda x: x.name.strip().lower() == ppt.name.strip().lower()
            )
            if similar:
                raise ValidationError(
                    _(
                        "There's another process with similar names "
                        "New: '%s' vs Existing: '%s'!"
                    )
                    % (ppt.name, similar.mapped("name"))
                )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The name must be unique!"),
    ]
