# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    cr.execute(
        """
        ALTER TABLE sale_advance_payment_inv
        RENAME date_invoice TO invoice_date
        """
    )
    cr.execute(
        """
        UPDATE ir_model_fields
        SET name = 'invoice_date'
        WHERE name = 'date_invoice' AND model = 'sale.advance.payment.inv'
        """
    )
    cr.execute(
        """
        UPDATE ir_translation
        SET name = 'sale.advance.payment.inv,invoice_date'
        WHERE name = 'sale.advance.payment.inv,date_invoice' AND type = 'model'
        """
    )
