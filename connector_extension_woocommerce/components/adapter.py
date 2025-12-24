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

    # # TODO: remove this total items and use the res.headers instead
    # def _get_res_total_items(self, res):
    #     headers = res.headers
    #     total_items = headers.get("X-WP-Total") or 0
    #     if total_items:
    #         total_items = int(headers.get("X-WP-Total"))
    #     return total_items

    # TODO: Remove *args and *kwargs and put params=None
    #       Check other methods than get to see if it'll work for them too
    def _exec_wcapi_call(self, op, resource, *args, **kwargs):  # noqa: C901
        if self.backend_record.enable_call_logging:
            _logger.info(
                "WooCommerce API Call - OP: %s, Resource: %s, Args: %s, KWArgs: %s",
                op,
                resource,
                args,
                kwargs,
            )

        # WooCommerce has the parameter next on the response headers
        # to get the next page but we can't use it because if we use
        # the offset, the next page will have the same items as the first page.
        # It looks like a bug in WooCommerce API.
        # So the 'page' parameter is incompatible with 'offset' parameter.
        # If 'offset' and 'page' are used at the same this, only 'offset'
        # will be taken into account and the 'page' will be ignored.
        params = kwargs.get("params", {})
        if {"page", "offset"}.issubset(params):
            raise ValidationError(
                _(
                    "The 'offset' and 'page' parameters are incompatible "
                    "in WooCommerce API calls. Please, use only one of them."
                )
            )

        func = getattr(self.wcapi, op)
        try:
            response = func(resource, *args, **kwargs)
            res_data = response.json()
            result = {
                "data": None,
                "returned_items": 0,
                "total_items": 0,
                "total_pages": 0,
                # "next": None,
                # "prev": None,
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
                    # for link in response.links.keys():
                    #     if link in ["next", "prev", "first", "last"]:
                    #         raise ValidationError(
                    #             _(
                    #                 "The '%s' link should not be present in singleton "
                    #                 "responses: %s"
                    #             )
                    #             % (link, res_data)
                    #         )
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
                    if op == "get":
                        result["data"] = res_data
                        result["total_items"] = int(response.headers["X-WP-Total"])
                        result["total_pages"] = int(response.headers["X-WP-TotalPages"])
                        # if "next" in response.links:
                        #     result["next"] = response.links["next"]["url"]
                        # if "prev" in response.links:
                        #     result["prev"] = response.links["prev"]["url"]
                    else:
                        raise ValidationError(
                            _("Unexpected multi-response for operation '%s': %s")
                            % (op, res_data)
                        )
                result["returned_items"] = len(result["data"])
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

        if self.backend_record.enable_call_logging:
            result_debug = dict(result)
            result_debug.pop("data")
            _logger.info("WooCommerce API Response: %s", result_debug)
        return result

    # def get_total_items(self, resource, domain=None):
    #     filters_values = self._get_search_fields()
    #     real_domain, common_domain = self._extract_domain_clauses(
    #         domain, filters_values
    #     )
    #     params = self._domain_to_normalized_dict(real_domain)
    #     if not common_domain:
    #         params["per_page"] = 1
    #     result = self._exec_wcapi_call("get", resource, params=params)
    #
    #     if not common_domain:
    #         return result["total_items"]
    #     else:
    #         # TODO: bnioe sta be, perque el _exec_wcapi_call no retorna sempre tot!!!
    #          # cal unsa fucnio intermitja
    #         return len(self._filter(result['data'], common_domain))

    def _get_search_fields(self):
        return ["modified_after"]  # , "offset", "per_page", "page"]

    # TODO: User API params search and search_fields to find for some fields like
    #       name, etc. This is a ilike contain %name% search so we need _filter
    #       as well but on a lot less records
    def _exec_get(self, resource, domain=None, offset=0, limit=None, count=False):
        if resource == "system_status":
            return self._exec_wcapi_call("get", resource)  # , *args, **kwargs)
        # get the domain
        if domain is None:
            domain = []
        search_fields = self._get_search_fields()
        real_domain, common_domain = self._extract_domain_clauses(domain, search_fields)

        # get the api call parameters
        params = self._domain_to_normalized_dict(real_domain)
        # per_page (records per page)
        if "per_page" in params:
            raise ValidationError(
                _(
                    "The 'per_page' parameter is managed automatically "
                    "in WooCommerce API calls. Do not use it "
                    "in the domain."
                )
            )
        page_size = self.backend_record.page_size
        if page_size > 0:
            params["per_page"] = page_size
        if offset < 0:
            offset = 0
        if count:
            params["_fields"] = "id"  # only need the ids to count

        seen_ids = set()
        all_data = []
        counter = 0
        while True:
            res = self._exec_wcapi_call(
                "get",
                resource,
                params={
                    **params,
                    "offset": offset,
                },
            )
            if res["returned_items"] == 0:
                break
            data = [d for d in res["data"] if d["id"] not in seen_ids]
            seen_ids |= {d["id"] for d in data}
            data = self._filter(data, *common_domain)
            data_count = len(data)
            if limit is not None:
                if limit < 0:
                    limit = 0
                if (counter + data_count) >= limit:
                    diff = limit - counter
                    all_data += data[:diff]
                    counter += diff
                    break
            counter += data_count
            if not count:
                all_data += data
            offset += res["returned_items"]

        if count:
            return counter
        else:
            return all_data

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
