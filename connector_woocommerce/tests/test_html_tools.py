# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import BaseCase

from odoo.addons.connector_woocommerce.common.tools import is_blank_html, prepare_html

# What the HTML editor leaves in a field nobody typed in, and its variants.
BLANK_VALUES = [
    "",
    False,
    " \n\t ",
    "<p></p>",
    "<p><br></p>",
    "<p><br></p><p><br></p>",
    "<p>&nbsp;</p>",
    '<div><p><span style="color: red;"><br></span></p></div>',
    "<br>",
    "<b></b>",
]

# Values with something to show, including the ones the rule must not judge.
CONTENT_VALUES = [
    "text",
    "<p>a<br>b</p>",
    '<p><img src="x"></p>',
    '<iframe src="x"></iframe>',
    "<table><tr><td></td></tr></table>",
    "<hr>",
    "<p>unclosed",
    "<<>>",
]


class TestHtmlTools(BaseCase):
    def test_is_blank_html_blank(self):
        for value in BLANK_VALUES:
            with self.subTest(value=value):
                self.assertTrue(is_blank_html(value))

    def test_is_blank_html_content(self):
        for value in CONTENT_VALUES:
            with self.subTest(value=value):
                self.assertFalse(is_blank_html(value))

    def test_prepare_html_blank(self):
        for value in BLANK_VALUES:
            with self.subTest(value=value):
                self.assertIsNone(prepare_html(value))

    def test_prepare_html_content(self):
        self.assertEqual(prepare_html("<p>a</p>"), "<p>a</p>")
        self.assertEqual(
            prepare_html('<p style="color: rgb(255, 0, 0);">a</p>'),
            '<p style="color: #FF0000;">a</p>',
        )
