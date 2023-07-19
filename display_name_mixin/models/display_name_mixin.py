# Copyright NuoBiT Solutions SL (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class DisplayNameMixin(models.Model):
    _name = "display.name.mixin"
    _description = "Display Name Mixin"

    def generate_generic_name(self, struct, transf=None, incl_fields=None):
        if not struct:
            return None
        if isinstance(struct, list):
            separator, fields = struct[0], struct[1:]
            new_data = list(
                filter(
                    lambda x: x is not None,
                    [
                        self.generate_generic_name(
                            x, transf=transf, incl_fields=incl_fields
                        )
                        for x in fields
                    ],
                )
            )
            return separator.join(new_data) if new_data else None
        else:
            value = None
            if incl_fields is None or struct in incl_fields:
                if transf and struct in transf:
                    value = transf[struct](self)
                else:
                    value = self[struct]
            return value
