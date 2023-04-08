# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from lxml import etree

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    @api.model
    def generate_address_block(self, parent_node, partner, gen_args):
        res = super().generate_address_block(parent_node, partner, gen_args)
        if self.journal_id.bank_id.is_sabadell:
            values = []
            # partner street
            if partner.street:
                partner_street = self._prepare_field(
                    "Adress Line1",
                    "partner.street",
                    {"partner": partner},
                    gen_args=gen_args,
                )
            else:
                partner_street = " " * 50
            values.append(f"{partner_street[:50]:<50}")
            if (
                gen_args.get("pain_flavor").startswith("pain.001.001.")
                or gen_args.get("pain_flavor").startswith("pain.008.001.")
                and (partner.zip or partner.city)
            ):
                # partner zip
                if partner.zip:
                    partner_zip = self._prepare_field(
                        "zip",
                        "partner.zip",
                        {"partner": partner},
                        gen_args=gen_args,
                    )
                else:
                    partner_zip = " " * 5
                values.append(f"{partner_zip[:5]:<5}")
                # partner city
                if partner.city:
                    partner_city = self._prepare_field(
                        "city",
                        "partner.city",
                        {"partner": partner},
                        gen_args=gen_args,
                    )
                else:
                    partner_city = " " * 45
                values.append(f"{partner_city[:45]:<45}")
                # partner state
                if partner.state_id:
                    partner_state = self._prepare_field(
                        "state",
                        "state.display_name",
                        {"state": partner.state_id},
                        gen_args=gen_args,
                    )
                    values.append(partner_state)
            # populate AdrLine
            if values:
                adr_line_max_len = 70
                adr_line_str = "".join(values).rstrip()[: adr_line_max_len * 2]
                if adr_line_str:
                    pstl_adr_l = parent_node.xpath("PstlAdr")
                    if not pstl_adr_l:
                        pstl_adr = etree.SubElement(parent_node, "PstlAdr")
                    else:
                        if len(pstl_adr_l) > 1:
                            raise ValidationError(
                                _(
                                    "Internal error: Expected one 'PstlAdr' tag, found %i"
                                )
                                % len(pstl_adr_l)
                            )
                        pstl_adr = pstl_adr_l[0]
                        for adr_line in pstl_adr.xpath("AdrLine"):
                            pstl_adr.remove(adr_line)
                    for i in range(0, len(adr_line_str), adr_line_max_len):
                        adr_line_part = etree.SubElement(pstl_adr, "AdrLine")
                        adr_line_part.text = adr_line_str[i : i + adr_line_max_len]
        return res
