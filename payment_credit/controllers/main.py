# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request

#from openerp.addons.website_sale.controllers.main import website_sale

from openerp.addons import website_sale

_logger = logging.getLogger(__name__)


class credit_controller(http.Controller):
    _accept_url = '/payment/credit/feedback'

    @http.route(['/payment/credit/feedback',], type='http', auth='none')
    def credit_form_feedback(self, **post):
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        request.registry['payment.transaction'].form_feedback(cr, uid, post, 'credit', context)
        return werkzeug.utils.redirect(post.pop('return_url', '/'))


class website_sale(website_sale.controllers.main.website_sale):
    """
    @http.route(['/shop/payment/transaction/<int:acquirer_id>'], type='json',
                auth="public", website=True)
    def payment_transaction(self, acquirer_id):
        return super(website_sale, self).payment_transaction(acquirer_id)
    """

    @http.route('/shop/payment/get_status/<int:sale_order_id>', type='json', auth="public", website=True)
    def payment_get_status(self, sale_order_id, **post):
        res = super(website_sale, self).payment_get_status(sale_order_id, **post)

        tx_obj = request.env['sale.order'].browse(sale_order_id).payment_tx_id
        if tx_obj.acquirer_id.provider == 'credit':
            if res['state']== 'done':
                #message = '<p>%s</p>' % _('Your payment has been received.')
                res['message'] = None

        return res
