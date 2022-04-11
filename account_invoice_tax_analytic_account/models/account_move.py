# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Miquel Raïch <miquel.raich@forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _preprocess_taxes_map(self, taxes_map):
        res = super()._preprocess_taxes_map(taxes_map)
        for taxes_map_entry in res:
            if res[taxes_map_entry]["tax_line"]:
                grouping_dict = self._get_tax_grouping_key_from_tax_line(
                    res[taxes_map_entry]["tax_line"]
                )
                res[taxes_map_entry]["tax_line"].update(
                    {
                        "origin_analytic_account_id": grouping_dict[
                            "analytic_account_id"
                        ],
                        "origin_analytic_tag_ids": grouping_dict["analytic_tag_ids"],
                    }
                )
            else:
                grouping_dict = res[taxes_map_entry]["grouping_dict"]
                res[taxes_map_entry]["grouping_dict"].update(
                    {
                        "origin_analytic_account_id": grouping_dict[
                            "analytic_account_id"
                        ],
                        "origin_analytic_tag_ids": grouping_dict["analytic_tag_ids"],
                    }
                )
        return res

    @api.model
    def _get_tax_grouping_key_from_tax_line(self, tax_line):
        res = super()._get_tax_grouping_key_from_tax_line(tax_line)
        if (
            not res.get("analytic_account_id")
            and tax_line.analytic_account_id
            and res["account_id"] == tax_line.account_id.id
        ):
            res["analytic_account_id"] = tax_line.analytic_account_id.id
        if (
            not res.get("analytic_tag_ids")
            and tax_line.analytic_tag_ids
            and res["account_id"] == tax_line.account_id.id
        ):
            res["analytic_tag_ids"] = [6, 0, tax_line.analytic_tag_ids.ids]
        return res

    @api.model
    def _get_tax_grouping_key_from_base_line(self, base_line, tax_vals):
        res = super()._get_tax_grouping_key_from_base_line(base_line, tax_vals)
        if (
            not res.get("analytic_account_id")
            and base_line.analytic_account_id
            and res["account_id"] == base_line.analytic_account_id.id
        ):
            res["analytic_account_id"] = base_line.analytic_account_id.id
        if (
            not res.get("analytic_tag_ids")
            and base_line.analytic_tag_ids
            and res["account_id"] == base_line.account_id.id
        ):
            res["analytic_tag_ids"] = [(6, 0, base_line.analytic_tag_ids.ids)]
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    origin_analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Analytic account Origin"
    )
    origin_analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        relation="account_move_origin_analytic_tag_rel",
        column1="move_id",
        column2="tag_id",
        string="Analytic tags Origin",
    )
