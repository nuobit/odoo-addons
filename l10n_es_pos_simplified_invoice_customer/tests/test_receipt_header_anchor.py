# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests import TransactionCase
from odoo.tools.misc import file_path
from odoo.tools.template_inheritance import apply_inheritance_specs

POINT_OF_SALE = (
    "point_of_sale/static/src/app/screens/receipt_screen/receipt/receipt_header/"
    "receipt_header.xml"
)
L10N_ES_POS = (
    "l10n_es_pos/static/src/overrides/components/receipt_header/receipt_header.xml"
)
OURS = (
    "l10n_es_pos_simplified_invoice_customer/static/src/overrides/components/"
    "receipt_header/receipt_header.xml"
)


class TestReceiptHeaderAnchor(TransactionCase):
    def _template(self, path):
        # The one template of the file
        (template,) = etree.parse(file_path(path)).getroot().iterchildren("t")
        return template

    def _another_extension(self, added):
        # What another module adds to the customer block's condition, the way a
        # module extends a condition (an «add» of the attribute, which joins it
        # without parentheses)
        return [
            etree.fromstring(
                "<xpath"
                " expr=\"//t[contains(@t-if, 'props.data.simplified_partner_id')]\""
                ' position="attributes">'
                f'<attribute name="t-if" add="{added}" separator=" "/>'
                "</xpath>"
            )
        ]

    def test_rule_holds_over_another_extension(self):
        # A module that changes the customer block's condition, whichever way
        # and whether it extends the template before or after this module,
        # leaves the block, with its condition as that module made it, inside
        # this module's own, unchanged
        (wrapper,) = self._template(OURS).xpath("xpath/t")
        rule = wrapper.get("t-if")
        for added in ("and another_condition", "or another_condition"):
            for another_first in (True, False):
                with self.subTest(added=added, another_first=another_first):
                    header = apply_inheritance_specs(
                        self._template(POINT_OF_SALE),
                        list(self._template(L10N_ES_POS)),
                    )
                    (block,) = header.xpath(
                        "//t[contains(@t-if, 'props.data.simplified_partner_id')]"
                    )
                    condition = f"{block.get('t-if')} {added}"
                    extensions = [
                        self._another_extension(added),
                        list(self._template(OURS)),
                    ]
                    if not another_first:
                        extensions.reverse()
                    for extension in extensions:
                        header = apply_inheritance_specs(header, extension)
                    (block,) = header.xpath(
                        "//t[contains(@t-if, 'props.data.simplified_partner_id')]"
                    )
                    self.assertEqual(block.get("t-if"), condition)
                    self.assertEqual(block.getparent().get("t-if"), rule)
