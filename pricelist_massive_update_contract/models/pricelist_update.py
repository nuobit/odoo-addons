# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class PriceListUpdate(models.Model):
    _inherit = "pricelist.update"

    update_pricelists = fields.Boolean(
        string="Update Price Lists",
        default=True,
    )
    update_contracts = fields.Boolean(
        string="Update Contract Prices",
    )

    def update_price_list_price(self):
        def has_price_list_tags(line, price_list_tags):
            return (
                line.contract_id.partner_id.property_product_pricelist.price_list_tag_ids
                & price_list_tags
            )

        for record in self:
            if not record.update_pricelists and not record.update_contracts:
                raise ValidationError(
                    _(
                        "You must select at least one update option "
                        "(Pricelists, Contracts or both)"
                    )
                )
            if record.update_pricelists:
                super().update_price_list_price()
            if record.update_contracts:
                all_contract_lines = self.env["contract.line"].search(
                    [
                        (
                            "contract_id.company_id",
                            "=",
                            record.company_id.id,
                        ),
                        ("contract_id.contract_type", "=", "sale"),
                    ]
                )
                contract_lines = all_contract_lines.filtered(
                    lambda x: has_price_list_tags(x, record.price_list_tag_ids)
                )
                for line in contract_lines:
                    line.price_unit = line.price_unit * (1 + record.percentage / 100)
                if contract_lines:
                    record.state = "processed"
