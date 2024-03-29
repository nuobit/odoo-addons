# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError


def pre_init_hook_barcode_check(cr):
    """This hook will look to see if any conflicting internal references exist
    before the module is installed
    :param odoo.sql_db.Cursor cr:
        Database cursor.
    """
    with cr.savepoint():
        cr.execute(
            """
            SELECT distinct t0.company_id, p0.barcode
            FROM product_product p0, product_template t0
            WHERE p0.product_tmpl_id = t0.id AND
                EXISTS (
                    SELECT 1
                    FROM product_product p1, product_template t1
                    WHERE p1.product_tmpl_id = t1.id AND
                        t1.company_id = t0.company_id AND
                        p1.barcode = p0.barcode AND p1.id != p0.id
                )"""
        )

        products = sorted(["[%i] %s" % p for p in cr.fetchall()])
        if products:
            raise ValidationError(
                _("Conflicting barcodes exist: %s" % ", ".join(products))
            )
