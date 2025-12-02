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
        self, op, res_data, res, resource, *args, raise_on_error=True, **kwargs
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
                # elif res_data.get("code") == "woocommerce_rest_term_invalid":
                #     error_message = _(
                #         "Error: '%s'. Probably the %s has been "
                #         "removed from Woocommerce. "
                #         "If it's the case, try to remove the binding of the %s."
                #         % (res_data.get("message"), resource, self.model._name)
                #     )
                # elif (
                #     res_data.get("code")
                #     == "woocommerce_rest_product_variation_invalid_parent"
                # ):
                #     error_message = _(
                #         "Error: '%s'. Probably the product in %s "
                #         "has been removed from Woocommerce. "
                #         "If it's the case, try to remove the binding of the "
                #         "woocommerce.product.template"
                #         % (
                #             res_data.get("message"),
                #             resource,
                #         )
                #     )
            elif res.status_code == 400:
                if res_data.get("code") == "term_exists":
                    error_message = _(
                        "Error: '%s'. Probably repeated record already exists in Woocommerce.\n"
                        "Please, review the data in %s/%s and compare it with %s"
                        % (
                            res_data["message"],
                            resource,
                            res_data["data"]["resource_id"],
                            kwargs["data"],
                        )
                    )
                # elif res_data.get("code") in [
                #     "woocommerce_rest_product_variation_invalid_id",
                #     "woocommerce_rest_product_invalid_id",
                # ]:
                #     error_message = _(
                #         "Error: '%s'. Probably the %s has been removed from Woocommerce. "
                #         "If it's the case, try to remove the binding of the %s."
                #         % (res_data.get("message"), resource, self.model._name)
                #     )
            if not error_message:
                error_message = _(
                    "Error: %s -> Op: %s, Resource: %s, Args: %s, KWArgs: %s"
                    % (res_data, op, resource, args, kwargs)
                )
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

    def _exec_wcapi_call(self, op, resource, *args, **kwargs):  # noqa: C901
        func = getattr(self.wcapi, op)
        try:
            response = func(resource, *args, **kwargs)
            res_data = response.json()
            result = {
                "data": None,
                "total_items": 0,
                "total_pages": 0,
                "next": None,
                "prev": None,
            }
            if not response.ok:
                # These are the cases where a not found should be an empty result
                # instead of an error, we need to bypass the standard REST behaviour
                # and make it look like more like an SQL whre if the parameters are wrong
                # it just returns no value
                if op == "get":
                    if response.status_code != 404 or res_data["code"] not in (
                        "woocommerce_rest_product_invalid_id",
                        "woocommerce_rest_product_variation_invalid_id",
                        "woocommerce_rest_product_variation_invalid_parent",
                        "woocommerce_rest_term_invalid",
                    ):
                        self._manage_error_codes(
                            op, res_data, response, resource, *args, **kwargs
                        )
                    result["data"] = []
                else:
                    self._manage_error_codes(
                        op, res_data, response, resource, *args, **kwargs
                    )
                    result["data"] = {}
            else:
                # check if the response is a singleton or a list
                if isinstance(res_data, dict):
                    singleton = True
                elif isinstance(res_data, list):
                    singleton = False
                else:
                    raise ValidationError(
                        _("Unexpected response from WooCommerce: %s") % res_data
                    )
                # check consistency between headers and response type
                multi_headers = ["X-WP-Total", "X-WP-TotalPages"]
                if singleton:
                    for header in multi_headers:
                        if header in response.headers:
                            raise ValidationError(
                                _(
                                    "The '%s' header should not be present in "
                                    "singleton responses: %s"
                                )
                                % (header, res_data)
                            )
                    for link in response.links.keys():
                        if link in ["next", "prev", "first", "last"]:
                            raise ValidationError(
                                _(
                                    "The '%s' link should not be present in singleton "
                                    "responses: %s"
                                )
                                % (link, res_data)
                            )
                else:
                    for header in multi_headers:
                        if header not in response.headers:
                            raise ValidationError(
                                _("The '%s' header is missing in multi responses: %s")
                                % (header, res_data)
                            )
                if singleton:
                    if op == "get":
                        result["data"] = [res_data]
                    else:
                        result["data"] = res_data
                    result["total_items"] = 1
                    result["total_pages"] = 1
                else:
                    result["data"] = res_data
                    result["total_items"] = int(response.headers["X-WP-Total"])
                    result["total_pages"] = int(response.headers["X-WP-TotalPages"])
                    if "next" in response.links:
                        result["next"] = response.links["next"]["url"]
                    if "prev" in response.links:
                        result["prev"] = response.links["prev"]["url"]
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
                    response.url,
                    response.request.headers,
                    response.request.method,
                    response.text and response.text[:100] + " ...",
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

        limit = kwargs.pop("limit", None)
        if limit is None:
            limit = self.get_total_items(resource, domain)

        all_data = []
        if limit > 0:
            params = self._domain_to_normalized_dict(real_domain)
            offset = kwargs.pop("offset", 0) or 0
            params["offset"] = offset if offset >= 0 else 0
            page_size = self.backend_record.page_size
            params["per_page"] = limit if page_size < 0 else page_size
            count = 0
            end = False
            while not end:
                if limit is not None:
                    if count + page_size > limit:
                        diff = limit - count
                        if diff <= 0:
                            raise ValidationError(
                                _(
                                    "Unexpected error in pagination diff: %s, count: %s, "
                                    "page_size: %s, limit: %s, params: %s"
                                )
                                % (
                                    diff,
                                    count,
                                    page_size,
                                    limit,
                                    params,
                                )
                            )
                        params["per_page"] = diff
                        end = True
                res = self._exec_wcapi_call(
                    "get", resource, params=params, *args, **kwargs
                )
                all_data += res["data"]
                if params["per_page"] != len(res["data"]):
                    raise ValidationError(
                        _(
                            "Unexpected error in pagination. The number of items "
                            "retrieved is different than the number aked."
                        )
                    )
                count += len(res["data"])
                params["offset"] += len(res["data"])
        return self._filter(all_data, common_domain)

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
            version = system_status["data"].get("environment", {}).get("version")
        return version
