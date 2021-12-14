# Copyright 2015 AvanzOSC - Ainara Galdona
# Copyright 2015-2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

MODEL_MAP = {
    "special": "l10n.es.aeat.mod303.prorrate.report",
}


class L10nEsAeatMod303Report(models.Model):
    _inherit = "l10n.es.aeat.mod303.report"

    vat_prorrate_type = fields.Selection(
        [("none", "None"), ("special", "Special prorrate")],
        # ('general', 'General prorrate'), ],
        readonly=True,
        states={"draft": [("readonly", False)]},
        string="VAT prorrate type",
        default="none",
        required=True,
    )

    casilla_43 = fields.Float(
        string=u"[43] Regularización de bienes de inversión",
        default=0,
        states={"done": [("readonly", True)]},
        help=u"Regularización por prorrata en bienes de inversión.",
    )

    casilla_44 = fields.Float(
        string=u"[44] Regularización de la prorrata",
        default=0,
        states={"done": [("readonly", True)]},
        help=u"Regularización por aplicación del porcentaje definitivo de "
        u"prorrata.",
    )

    @api.multi
    def _calculate_casilla_44(self):
        self.ensure_one()

        if not self.child.first_reg_move_id:
            raise ValidationError(_("First regularization move is not created"))

        self.casilla_44 = self.child.first_reg_amount

    @api.multi
    def calculate(self):
        res = super(L10nEsAeatMod303Report, self).calculate()
        for report in self:
            report.casilla_44 = 0
            if report.vat_prorrate_type != "special" or report.period_type not in (
                "4T",
                "12",
            ):
                continue
            report._calculate_casilla_44()
        return res

    def _get_child_model(self):
        self.ensure_one()
        if self.vat_prorrate_type == "none":
            raise ValidationError(_("No settings for none prorrate"))
        return MODEL_MAP[self.vat_prorrate_type]

    @property
    def child(self):
        self.ensure_one()
        childs = self.env[self._get_child_model()].search(
            [
                ("parent_id", "=", self.id),
            ]
        )
        if len(childs) > 1:
            raise ValidationError(
                _(
                    "Inconsistency detected. More than one "
                    "childs found for the same parent"
                )
            )
        return childs

    def prorrate_config_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": self._get_child_model(),
            "views": [[False, "form"]],
            "context": not self.child and {"default_parent_id": self.id},
            "res_id": self.child.id,
            "target": "new",
        }
