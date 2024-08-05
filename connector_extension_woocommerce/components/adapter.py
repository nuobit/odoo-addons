# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

import json
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

    def _manage_error_codes(
        self, res_data, res, resource, raise_on_error=True, **kwargs
    ):
        if not res.ok:
            error_message = None
            if res.status_code == 404:
                if res_data.get("code") == "rest_no_route":
                    error_message = _(
                        "Error: '%s'. Probably the %s has been"
                        " removed from Woocommerce. "
                        "If it's the case, try to remove the binding of the %s."
                        % (res_data.get("message"), resource, self.model._name)
                    )
                elif res_data.get("code") == "woocommerce_rest_term_invalid":
                    error_message = _(
                        "Error: '%s'. Probably the %s has been "
                        "removed from Woocommerce. "
                        "If it's the case, try to remove the binding of the %s."
                        % (res_data.get("message"), resource, self.model._name)
                    )
                elif (
                    res_data.get("code")
                    == "woocommerce_rest_product_variation_invalid_parent"
                ):
                    error_message = _(
                        "Error: '%s'. Probably the product in %s "
                        "has been removed from Woocommerce. "
                        "If it's the case, try to remove the binding of the "
                        "woocommerce.product.template"
                        % (
                            res_data.get("message"),
                            resource,
                        )
                    )
            elif res.status_code == 400:
                if res_data.get("code") == "term_exists":
                    error_message = _(
                        "Error: '%s'. Probably repeated record already exists in Woocommerce.\n"
                        "Please, review the data in %s/%s and compare it with %s"
                        % (
                            res_data["message"],
                            resource,
                            res_data["res_data"]["resource_id"],
                            kwargs["data"],
                        )
                    )
                elif (
                    res_data.get("code")
                    == "woocommerce_rest_product_variation_invalid_id"
                ):
                    error_message = _(
                        "Error: '%s'. Probably the %s has been removed from Woocommerce. "
                        "If it's the case, try to remove the binding of the %s."
                        % (res_data.get("message"), resource, self.model._name)
                    )
            if not error_message:
                error_message = _("Error: %s, Resource: %s" % (res_data, resource))
            if raise_on_error:
                raise ValidationError(error_message)
            return error_message
        return res_data

    # TODO: remove this total items and use the res.headers instead
    def _get_res_total_items(self, res):
        headers = res.headers
        total_items = headers.get("X-WP-Total") or 0
        if total_items:
            total_items = int(headers.get("X-WP-Total"))
        return total_items

    def _exec_wcapi_call(self, op, resource, *args, **kwargs):
        func = getattr(self.wcapi, op)
        try:
            res = func(resource, *args, **kwargs)
            res_data = res.json()
            if "data" in res_data:
                res_data["res_data"] = res_data.pop("data")
            res_data = self._manage_error_codes(res_data, res, resource, **kwargs)
            total_items = self._get_res_total_items(res)
            result = {
                "ok": res.ok,
                "status_code": res.status_code,
                "total_items": total_items,
                "data": res_data,
            }
        except RequestConnectionError as e:
            raise RetryableJobError(_("Error connecting to WooCommerce: %s") % e) from e
        except json.decoder.JSONDecodeError as e:
            raise ValidationError(
                _(
                    "Error decoding json WooCommerce response: "
                    "%s\nArgs:%s\nKwargs:%s\n"
                    "URL:%s\nHeaders:%s\nMethod:%s\nBody:%s"
                )
                % (
                    e,
                    args,
                    kwargs,
                    res.url,
                    res.request.headers,
                    res.request.method,
                    res.text and res.text[:100] + " ...",
                )
            ) from e
        return result

    def get_total_items(self, resource, domain=None):
        filters_values = self._get_search_fields()
        real_domain, common_domain = self._extract_domain_clauses(
            domain, filters_values
        )
        params = self._domain_to_normalized_dict(real_domain)
        params["per_page"] = 1
        result = self._exec_wcapi_call("get", resource, params=params)
        return result["total_items"]

    def _get_search_fields(self):
        return ["modified_after", "offset", "per_page", "page"]

    def _exec_get(self, resource, *args, **kwargs):
        if resource == "system_status":
            return self._exec_wcapi_call("get", resource, *args, **kwargs)
        # WooCommerce has the parameter next on the response headers
        # to get the next page but we can't use it because if we use
        # the offset, the next page will have the same items as the first page.
        # It looks like a bug in WooCommerce API.
        domain = []
        if "domain" in kwargs:
            domain = kwargs.pop("domain")
        search_fields = self._get_search_fields()
        real_domain, common_domain = self._extract_domain_clauses(domain, search_fields)
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
            res = self._exec_wcapi_call("get", resource, params=params, *args, **kwargs)
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
        return self._exec_wcapi_call(
            "delete",
            resource,
            *args,
            **kwargs,
        )

    def _exec_options(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def get_version(self):
        system_status = self._exec("get", "system_status")
        version = False
        if system_status:
            version = system_status["data"].get("environment").get("version")
        return version
