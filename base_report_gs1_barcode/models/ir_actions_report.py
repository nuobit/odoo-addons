# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2022 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models

try:
    import pystrich.code128 as c128
    import pystrich.datamatrix as dmx

    class DataMatrixRendererMod(dmx.DataMatrixRenderer):
        def add_border(self, colour=1):
            self.quiet_zone = 0
            return super().add_border(colour=colour)

    dmx.DataMatrixRenderer = DataMatrixRendererMod

except ImportError:
    pass


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def barcode(
        self,
        barcode_type,
        value,
        width=600,
        height=100,
        humanreadable=0,
        quiet=1,
        mask=None,
        **kwargs,
    ):
        if barcode_type == "gs1-128":
            encoder = c128.Code128Encoder(
                value, options=dict(show_label=False, height=int(height))
            )
            return encoder.get_imagedata()
        elif barcode_type == "gs1-datamatrix":
            encoder = dmx.DataMatrixEncoder(value)
            return encoder.get_imagedata()
        else:
            return super().barcode(
                barcode_type,
                value,
                width=width,
                height=height,
                humanreadable=humanreadable,
                quiet=quiet,
                mask=mask,
            )
