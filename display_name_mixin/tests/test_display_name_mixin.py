# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase


class TestDisplayNameMixin(TransactionCase):
    def test_display_name_mixin_single(self):
        # ARRANGE
        incl_fields = ["field1", "field2", "field3", "field4", "field5"]
        transf = {field: (lambda x, f=field: f"{f}_value") for field in incl_fields}
        struct = [
            " | ",
            "field1",
            [" ", "field4", [" - ", "field2", "field3"]],
            "field5",
        ]

        # ACT
        result = self.env["display.name.mixin"].generate_generic_name(
            struct, transf=transf, incl_fields=incl_fields
        )

        # ASSERT
        self.assertEqual(
            result,
            "field1_value | field4_value field2_value - field3_value | field5_value",
        )
