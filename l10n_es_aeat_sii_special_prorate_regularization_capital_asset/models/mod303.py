# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, fields, models
from odoo.exceptions import ValidationError


class L10nEsAeatMod303Report(models.AbstractModel):
    _inherit = "l10n.es.aeat.mod303.report"

    prorate_asset_lines_to_send = fields.One2many(
        comodel_name="capital.asset.prorate.regularization",
        compute="_compute_prorate_asset_lines_to_send",
    )

    def _compute_prorate_asset_lines_to_send(self):
        for rec in self:
            rec.prorate_asset_lines_to_send = (
                rec.capital_asset_prorate_regularization_line_ids.filtered(
                    lambda x: x.sii_state not in ["sent"]
                )
            )

    prorate_asset_lines_to_cancel = fields.One2many(
        comodel_name="capital.asset.prorate.regularization",
        compute="_compute_prorate_asset_lines_to_cancel",
    )

    def _compute_prorate_asset_lines_to_cancel(self):
        for rec in self:
            rec.prorate_asset_lines_to_cancel = (
                rec.capital_asset_prorate_regularization_line_ids.filtered(
                    lambda x: x.sii_state not in ["cancelled", "not_sent"]
                )
            )

    def send_sii(self):
        for report in self:
            if (
                self.move_prorate_capital_asset_id
                and self.move_prorate_capital_asset_id.state == "draft"
            ):
                raise ValidationError(
                    _(
                        "Please, post capital asset prorate move of the 303 model "
                        "before send capital asset prorate regularization to SII"
                    )
                )
            for line in report.prorate_asset_lines_to_send:
                line.send_asset_sii()

    def cancel_sii(self):
        for report in self:
            for line in report.prorate_asset_lines_to_cancel:
                line.cancel_asset_sii()

    def button_unpost(self):
        if self.prorate_asset_lines_to_cancel:
            raise ValidationError(
                _(
                    "Exist prorate lines in year: %s in assets %s with "
                    "capital asset prorate lines. "
                    "Please send the cancellation to the sii before canceling the 303 model."
                )
                % (self.year, self.prorate_asset_lines_to_cancel)
            )
        self.cancel_sii()
        super().button_unpost()
