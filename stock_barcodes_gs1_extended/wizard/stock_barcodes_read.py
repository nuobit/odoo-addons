# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, _

import re


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = 'wiz.stock.barcodes.read'

    def process_barcode(self, barcode):
        """ Only has been implemented AI (01, 02, 10, 21, 37), so is possible that
        scanner reads a barcode ok but this one is not precessed.
        """
        try:
            barcode_decoded = self.env['gs1_barcode'].decode(barcode)
        except Exception:
            return super().process_barcode(barcode)

        contained_product_barcode = barcode_decoded.get('02', False)
        if contained_product_barcode:
            return super().process_barcode(barcode)

        processed = False
        product_barcode = barcode_decoded.get('01', False)
        if not product_barcode:
            # Sometimes the product does not yet have a GTIN. In this case
            # try the AI 240 'Additional product identification assigned
            # by the manufacturer'.
            product_barcode = barcode_decoded.get('240', False)

        if product_barcode:
            m = re.match(r'^0*([0-9]+)$', product_barcode)
            if not m:
                self._set_messagge_info(
                    'not_found', _('Barcode %s is not a GTIN') % product_barcode)
                return False
            product_barcode_trim = m.group(1)

            product = self.env['product.product'].search([
                ('company_id', '=', self.env.user.company_id.id),
                ('barcode', '=like', '%' + product_barcode_trim),
            ])
            if not product:
                self._set_messagge_info(
                    'not_found', _('Barcode for product %s not found') % product.display_name)
                return False
            else:
                if len(product) != 1:
                    self._set_messagge_info(
                        'more_match',
                        _('More than one products found '
                          'for that barcode: %s') % product.mapped('display_name'))
                    return False
                m = re.match(r'^0*(%s)$' % product_barcode_trim, product.barcode)
                if not m:
                    self._set_messagge_info(
                        'not_found', _('Barcode for product %s not found') % product.display_name)
                    return False

                processed = True
                self.action_product_scaned_post(product)

        tracking_code = None
        if self.product_id.tracking == 'serial':
            serial_barcode = barcode_decoded.get('21', False)
            if serial_barcode:
                tracking_code = serial_barcode
        elif self.product_id.tracking == 'lot':
            lot_barcode = barcode_decoded.get('10', False)
            if lot_barcode:
                tracking_code = lot_barcode

        if tracking_code:
            lot = self.env['stock.production.lot'].search([
                ('name', '=', tracking_code),
                ('product_id', '=', self.product_id.id),
            ])
            if not lot:
                lot = self.env['stock.production.lot'].create({
                    'name': tracking_code,
                    'product_id': self.product_id.id,
                })
            self.lot_id = lot
            processed = True

        if processed:
            self.action_done()
            self._set_messagge_info('success', _('Barcode read correctly'))
            return True
        self._set_messagge_info('not_found', _('Barcode not found'))
        return False
