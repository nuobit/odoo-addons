# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT 2025 - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _
from odoo.exceptions import ValidationError


def internal_reference_duplicate_check(env):
    """This hook will look to see if any conflicting internal references exist before
    the module is installed
    :param Odoo env: Odoo environment
    """
    with env.cr.savepoint():
        env.cr.execute(
            """
            SELECT p0.id, p0.default_code, t0.company_id
            FROM product_product p0, product_template t0
            WHERE p0.product_tmpl_id = t0.id AND
                EXISTS (
                    SELECT 1
                    FROM product_product p1, product_template t1
                    WHERE p1.product_tmpl_id = t1.id AND
                        (t1.company_id is null OR t0.company_id is null OR
                             t1.company_id = t0.company_id) AND
                        p1.default_code = p0.default_code AND p1.id != p0.id
                )"""
        )
        products = sorted(["[%i] %s (%i)" % p for p in env.cr.fetchall()])
        if products:
            raise ValidationError(
                _("Conflicting internal references exist: {}").format(
                    ", ".join(products)
                )
            )
