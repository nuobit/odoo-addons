# Copyright NuoBiT Solutions SL - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.osv import expression
from odoo.osv.query import Query


class L10nEsAeatTaxLine(models.Model):
    _inherit = "l10n.es.aeat.tax.line"

    asset_ids = fields.Many2many(
        string="Assets",
        comodel_name="account.asset",
    )
    mod303_id = fields.Many2one(
        string="Model 303",
        comodel_name="l10n.es.aeat.mod303.report",
        compute="_compute_mod303_id",
        store=True,
    )
    mod303_period_type = fields.Selection(related="mod303_id.period_type")

    @api.depends("model", "res_id")
    def _compute_mod303_id(self):
        for rec in self:
            if rec.model == "l10n.es.aeat.mod303.report":
                rec.mod303_id = self.env[rec.model].browse(rec.res_id)
            else:
                rec.mod303_id = False

    @api.model
    def _search_mod303_id(self, operator, value):
        def is_record_id(v):
            # bool is a subclass of int: True would pass as the id 1
            return isinstance(v, int) and not isinstance(v, bool) and v > 0

        if operator not in ("=", "!=", "in", "not in"):
            raise NotImplementedError(
                _("Unsupported operator %s for Model 303 search") % operator
            )
        # A 303 tax line whose res_id is 0 has no 303, as in the compute. The negation
        # of this domain is its exact complement because model and res_id are
        # required, so never NULL
        mod303_domain = [
            "&",
            ("model", "=", "l10n.es.aeat.mod303.report"),
            ("res_id", "!=", 0),
        ]
        if operator == "in" and isinstance(value, Query):
            # A search on mod303_period_type: the 303 ids come as a subquery
            domain = expression.AND([mod303_domain, [("res_id", "in", value)]])
        else:
            # Alone, None means no 303 as False does, as in Odoo; inside a list Odoo
            # reads it otherwise, so there it is refused like any other value
            values = (
                [value if value is not None else False]
                if operator in ("=", "!=")
                else value
            )
            if not isinstance(values, (list, tuple)) or not all(
                v is False or is_record_id(v) for v in values
            ):
                raise NotImplementedError(
                    _("Unsupported value %s for Model 303 search") % repr(value)
                )
            report_ids = [v for v in values if v is not False]
            domain = expression.AND([mod303_domain, [("res_id", "in", report_ids)]])
            if len(report_ids) < len(values):
                # False among the values also asks for the lines without a 303
                domain = expression.OR(
                    [domain, [expression.NOT_OPERATOR] + mod303_domain]
                )
        return (
            [expression.NOT_OPERATOR] + domain
            if operator in ("!=", "not in")
            else domain
        )

    def get_calculated_assets(self):
        action_dict = (
            self.env.ref("account_asset_management.account_asset_action")
            .sudo()
            .read()[0]
        )
        action_dict["domain"] = [("id", "in", self.asset_ids.ids)]
        return action_dict
