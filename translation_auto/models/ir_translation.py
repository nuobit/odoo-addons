# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models

try:
    from googletrans import Translator
except ImportError:
    pass


class IrTranslation(models.Model):
    _inherit = "ir.translation"

    def translate_source_to_dest(self):
        self.ensure_one()

        trl = Translator().translate(text=self.source, src="en_US", dest=self.lang).text

        if self.source == self.source.capitalize():
            trl = trl.capitalize()

        self.value = trl
        self.state = "translated"

    def translate_dest_to_source(self):
        self.ensure_one()

        trl = Translator().translate(text=self.value, src=self.lang, dest="en_US").text

        if self.value == self.value.capitalize():
            trl = trl.capitalize()

        self.source = trl
        self.state = "translated"
