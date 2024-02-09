# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AssetProrateRegularization(models.Model):
    _name = "capital.asset.prorate.regularization"
    _description = "Capital Asset Prorate Regularization"

    year = fields.Integer(
        string="Year",
    )
    amount = fields.Float(
        string="Amount",
    )
    asset_id = fields.Many2one(
        comodel_name="account.asset",
        string="Asset",
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    prorate_percent = fields.Float(
        string="Prorate (%)",
    )
    mod303_id = fields.Many2one(
        comodel_name="l10n.es.aeat.mod303.report",
        string="Model 303",
        readonly=True,
        ondelete="restrict",
        index=True,
    )

    @api.constrains("year", "asset_id")
    def _check_year(self):
        for rec in self:
            other = self.env[self._name].search(
                [("asset_id", "=", rec.asset_id.id), ("year", "=", rec.year)]
            )
            if len(other) > 1:
                raise ValidationError(
                    _(
                        "There's another capital capital asset prorate regularization "
                        "with the same year: %s and asset: {%i} %s"
                    )
                    % (rec.year, rec.asset_id, rec.asset_id.name)
                )

    def _get_by_year(self, mod303):
        asset_regularization_line = self.filtered(lambda x: x.year == mod303.year)
        if asset_regularization_line:
            if not asset_regularization_line.mod303_id:
                raise ValidationError(
                    _(
                        "This asset have a prorate regularization"
                        " line this year: %s, but it's not related"
                        " with a model 303. Please, review prorate"
                        " regularizations of capital asset: %s"
                    )
                    % (mod303.year, self.mapped("asset_id.name"))
                )
            elif asset_regularization_line.mod303_id != mod303:
                raise ValidationError(
                    _(
                        "This asset have a prorate regularization"
                        " line this year: %s,"
                        " but related with another model 303. "
                        "Please, review prorate regularizations "
                        "of capital asset: %s"
                    )
                    % (mod303.year, self.mapped("asset_id.name"))
                )
        return asset_regularization_line

    def unlink(self):
        allow_delete_capital_asset_lines = self.env.context.get(
            "allow_delete_capital_asset_lines", False
        )
        for rec in self:
            if rec.mod303_id and not allow_delete_capital_asset_lines:
                raise ValidationError(
                    _(
                        "You can't delete a capital asset regularization line "
                        "if it's linked with a model 303."
                    )
                )
        super(AssetProrateRegularization, self).unlink()
