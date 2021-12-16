# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import ValidationError


def pre_init_hook_internal_reference_check(cr):
    """This hook will look to see if any conflicting internal references exist before
    the module is installed
    :param odoo.sql_db.Cursor cr:
        Database cursor.
    """
    with cr.savepoint():
        cr.execute("""SELECT distinct p0.company_id, p0.default_code 
                      FROM product_product p0
                      WHERE EXISTS (
                               SELECT 1
                               FROM product_product p1
                               where p1.company_id = p0.company_id and
                                     p1.default_code = p0.default_code AND 
                                     p1.id != p0.id
                            )
                      """)

        products = sorted(['[%i] %s' % p for p in cr.fetchall()])
        if products:
            raise ValidationError(
                _('Conflicting internal references exist: %s' % ', '.join(products))
            )
