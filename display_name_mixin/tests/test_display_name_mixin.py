# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase


class TestDisplayNameMixin(TransactionCase):
    def test_display_name_mixin_single(self):
        # ARRANGE
        incl_fields = ["field1", "field2", "field3", "field4", "field5"]
        transf = {
            "field1": lambda x: "field1_value",
            "field5": lambda x: "field5_value",
            "field4": lambda x: "field4_value",
            "field2": lambda x: "field2_value",
            "field3": lambda x: "field3_value",
        }
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
