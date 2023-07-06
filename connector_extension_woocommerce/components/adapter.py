# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WooCommerceAdapterCRUD(AbstractComponent):
    _name = "base.backend.woocommerce.adapter.crud"
    _inherit = "base.backend.adapter.crud"

    # TODO: manage retryable_errors
    def _exec(self, op, resource, *args, **kwargs):
        func = getattr(self, "_exec_%s" % op)
        return func(resource, *args, **kwargs)

    def get_total_items(self, resource, domain=None):
        filters_values = self._get_filters_values()
        real_domain, common_domain = self._extract_domain_clauses(
            domain, filters_values
        )
        res = self.wcapi.get(
            resource,
            params=self._domain_to_normalized_dict(real_domain),
        )
        total_items = int(res.headers.get("X-WP-Total"))
        return total_items

    def _get_filters_values(self):
        return ["modified_after", "offset", "per_page", "page"]

    def _exec_get(self, resource, *args, **kwargs):
        domain = []
        if "domain" in kwargs:
            domain = kwargs.pop("domain")
        filters_values = self._get_filters_values()
        real_domain, common_domain = self._extract_domain_clauses(
            domain, filters_values
        )
        params = self._domain_to_normalized_dict(real_domain)
        if "offset" in kwargs and "offset" not in params:
            params["offset"] = kwargs.pop("offset")
        if "limit" in kwargs and "per_page" not in params:
            if kwargs["limit"] < 0:
                # this 100 is the max of per_page on woocommerce
                kwargs.pop("limit")
                params["per_page"] = 100
            else:
                params["per_page"] = kwargs.pop("limit")
        res = self.wcapi.get(
            resource,
            *args,
            **kwargs,
            params=params,
        )
        res = res.json()
        if isinstance(res, dict):
            res = [res]
        res = self._filter(res, common_domain)
        return res

    def _exec_post(self, resource, *args, **kwargs):
        res = self.wcapi.post(resource, *args, **kwargs)
        if res.status_code in [400, 401, 403, 404, 500]:
            raise ValidationError(res.json().get("message"))
        try:
            res = res.json()
        except Exception as e:
            raise ValidationError(e) from e
        return res

    def _exec_put(self, resource, *args, **kwargs):
        return self.wcapi.put(resource, *args, **kwargs)

    def _exec_delete(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def _exec_options(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def get_version(self):
        system_status = self._exec("get", "system_status")
        version = False
        if system_status:
            version = system_status.get("environment").get("version")
        return version
