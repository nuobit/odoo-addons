# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from requests.exceptions import ConnectionError as RequestConnectionError

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import RetryableJobError

from ...connector_extension.common.tools import trim_domain

_logger = logging.getLogger(__name__)


class ConnectorExtensionWooCommerceAdapterCRUD(AbstractComponent):
    _name = "connector.extension.woocommerce.adapter.crud"
    _inherit = "connector.extension.adapter.crud"

    def _exec(self, op, resource, *args, **kwargs):
        if kwargs.get("domain"):
            kwargs["domain"] = trim_domain(kwargs["domain"])
        func = getattr(self, "_exec_%s" % op)
        return func(resource, *args, **kwargs)

    def _exec_wcapi_call(self, op, resource, *args, **kwargs):
        func = getattr(self.wcapi, op)
        try:
            res = func(resource, *args, **kwargs)
            data = res.json()
            if not res.ok and res.status_code == "rest_no_route":
                raise ValidationError(
                    _(
                        "Error: '%(message)s'. Probably the %(resource)s has been removed "
                        "from Woocommerce. If it's the case, try to remove the binding "
                        "of the %(model)s."
                    )
                    % dict(
                        message=res.get("message"),
                        resource=resource,
                        model=self.model._name,
                    )
                )
            elif not res.ok:
                raise ValidationError(data)
            headers = res.headers
            total_items = headers.get("X-WP-Total") or 0
            if total_items:
                total_items = int(headers.get("X-WP-Total"))
            result = {
                "ok": res.ok,
                "status_code": res.status_code,
                "total_items": total_items,
                "data": data,
            }
        except RequestConnectionError as e:
            raise RetryableJobError(_("Error connecting to WooCommerce: %s") % e) from e
        return result

    def get_total_items(self, resource, domain=None):
        filters_values = self._get_filters_values()
        real_domain, common_domain = self._extract_domain_clauses(
            domain, filters_values
        )
        params = self._domain_to_normalized_dict(real_domain)
        params["per_page"] = 1
        result = self._exec_wcapi_call("get", resource=resource, params=params)
        return result["total_items"]

    def _get_filters_values(self):
        return ["modified_after", "offset", "per_page", "page"]

    def _exec_get(self, resource, *args, **kwargs):
        if resource == "system_status":
            return self._exec_wcapi_call("get", resource=resource, *args, **kwargs)
        # WooCommerce has the parameter next on the response headers
        # to get the next page but we can't use it because if we use
        # the offset, the next page will have the same items as the first page.
        # It looks like a bug in WooCommerce API.
        domain = []
        if "domain" in kwargs:
            domain = kwargs.pop("domain")
        filters_values = self._get_filters_values()
        real_domain, common_domain = self._extract_domain_clauses(
            domain, filters_values
        )
        params = self._domain_to_normalized_dict(real_domain)
        if "limit" in kwargs:
            limit = kwargs.pop("limit")
        else:
            limit = self.get_total_items(resource, domain)
        params["offset"] = (
            kwargs.pop("offset") if "offset" in kwargs and "offset" not in params else 0
        )
        page_size = self.backend_record.page_size
        params["per_page"] = page_size if page_size > 0 else 100
        data = []
        while len(data) < limit:
            if page_size > limit - len(data):
                params["per_page"] = limit - len(data)
            res = self._exec_wcapi_call(
                "get", resource=resource, params=params, *args, **kwargs
            )
            # WooCommerce returns a dict if the response is a single item
            if not isinstance(res["data"], list):
                res["data"] = [res["data"]]
            data += res["data"]
            params["offset"] += len(res["data"])
        return self._filter(data, common_domain)

    def _exec_post(self, resource, *args, **kwargs):
        res = self._exec_wcapi_call(
            "post",
            resource,
            *args,
            **kwargs,
        )
        return res["data"]

    def _exec_put(self, resource, *args, **kwargs):
        return self._exec_wcapi_call("put", resource, *args, **kwargs)

    def _exec_delete(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def _exec_options(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def get_version(self):
        system_status = self._exec("get", "system_status")
        version = False
        if system_status:
            version = system_status["data"].get("environment").get("version")
        return version
