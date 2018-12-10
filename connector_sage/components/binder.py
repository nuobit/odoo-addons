# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ModelBinder(Component):
    """ Bind records and give odoo/sage ids correspondence

    Binding models are models called ``sage.{normal_model}``,
    like ``sage.res.partner`` or ``sage.product.product``.
    They are ``_inherits`` of the normal models and contains
    the Sage ID, the ID of the Sage Backend and the additional
    fields belonging to the Sage instance.
    """
    _name = 'sage.binder'
    _inherit = ['base.binder.composite', 'base.sage.connector']
    # _external_field = 'sage_id'

    _apply_on = [
        # 'prestashop.shop.group',
        # 'prestashop.shop',
        # 'sage.res.partner',
        # 'prestashop.address',
        # 'prestashop.res.partner.category',
        # 'prestashop.res.lang',
        # 'prestashop.res.country',
        # 'prestashop.res.currency',
        # 'prestashop.account.tax',
        # 'prestashop.account.tax.group',
        # 'prestashop.product.category',
        # 'prestashop.product.image',
        # 'prestashop.product.template',
        # 'prestashop.product.combination',
        # 'prestashop.product.combination.option',
        # 'prestashop.product.combination.option.value',
        # 'prestashop.sale.order',
        # 'prestashop.sale.order.state',
        # 'prestashop.delivery.carrier',
        # 'prestashop.refund',
        # 'prestashop.supplier',
        # 'prestashop.product.supplierinfo',
        # 'prestashop.mail.message',
        # 'prestashop.groups.pricelist',
    ]
