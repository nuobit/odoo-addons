# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import re

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class WooCommerceSaleOrderAdapter(Component):
    _inherit = "woocommerce.sale.order.adapter"

    def _prepare_meta_data_fields(self):
        meta_data_fields = super()._prepare_meta_data_fields()
        meta_data_fields.append("_wc_shipment_tracking_items")
        return meta_data_fields

    def _manage_error_codes(
        self, res_data, res, resource, raise_on_error=True, **kwargs
    ):
        if not res.ok:
            if res.status_code == 400:
                m = re.match("^[^:]+: (.+)$", res_data["message"])
                if (
                    m
                    and m.group(1) == "status"
                    and res_data["code"] == "rest_invalid_param"
                ):
                    error_message = _(
                        "Error: '%s'. Probably the state %s is not defined on Woocommerce. "
                        "Configure states in Woocommerce Advanced "
                        "Shippment Tracking (AST) settings."
                        % (res_data["message"], kwargs["data"]["status"])
                    )
                    if raise_on_error:
                        raise ValidationError(error_message)
                    else:
                        return error_message

        return super()._manage_error_codes(
            res_data, res, resource, raise_on_error, **kwargs
        )
