# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

import json
import logging

import requests

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import RetryableJobError

_logger = logging.getLogger(__name__)


class ConnectorExtensionWordpressAdapterCRUD(AbstractComponent):
    _name = "connector.extension.wordpress.adapter.crud"
    _inherit = "connector.extension.adapter.crud"

    def _exec(self, op, resource, *args, **kwargs):
        func = getattr(self, "_exec_%s" % op)
        return func(resource, *args, **kwargs)

    def _manage_error_codes(
        self, res_data, res, resource, raise_on_error=True, **kwargs
    ):
        if not res.ok:
            error_message = None
            if res.status_code == 404:
                if res_data.get("code") == "rest_post_invalid_id":
                    error_message = _(
                        "Error: '%s'. Probably the %s has been "
                        "removed from WordPress. "
                        "If it's the case, try to remove the binding of the %s."
                        % (res_data.get("message"), resource, self.model._name)
                    )
            elif res.status_code == 500:
                if res_data.get("code") == "rest_upload_sideload_error":
                    error_message = _(
                        "Error: '%s'. Probably the image or document "
                        "is uploaded with bad format. "
                        "Please, review on database: %s"
                        % (res_data["message"], kwargs["headers"])
                    )
            if not error_message:
                error_message = _("Error: %s, Resource: %s" % (res_data, resource))
            if raise_on_error:
                raise ValidationError(error_message)
            return error_message
        return res_data

    def _exec_wp_call(self, op, resource, *args, **kwargs):
        url = self.backend_record.url + "/wp-json/wp/v2/" + resource
        func = getattr(requests, op)
        try:
            res = func(url, *args, **kwargs)
            res_data = res.json()
            res_data = self._manage_error_codes(res_data, res, resource, **kwargs)
            result = {
                "ok": res.ok,
                "status_code": res.status_code,
                "headers": res.headers,
                "data": res_data,
            }
        except requests.exceptions.ConnectionError as e:
            raise RetryableJobError(_("Error connecting to WordPress: %s") % e) from e
        except json.JSONDecodeError as e:
            raise ValidationError(
                _("Error decoding json WordPress response: %s\n%s") % (e, res.text)
            ) from e
        return result

    def _get_search_fields(self):
        return ["modified_after", "offset", "per_page", "page"]

    def get_total_items(self, resource, domain=None):
        filters_values = self._get_search_fields()
        real_domain, common_domain = self._extract_domain_clauses(
            domain, filters_values
        )
        params = self._domain_to_normalized_dict(real_domain)
        # TODO: make an optimization to get the total items and use the result
        params["per_page"] = 1
        result = self._exec_wp_call(
            "get",
            resource,
            auth=(
                self.backend_record.consumer_key,
                self.backend_record.consumer_secret,
            ),
            params=params,
            verify=self.backend_record.verify_ssl,
        )

        total_items_header = result["headers"]._store.get("x-wp-total")
        if total_items_header:
            total_items_header = int(total_items_header[1])
        else:
            # WordPress returns a dict if the response is a single item
            if not isinstance(result["data"], list):
                result["data"] = [result["data"]]
            total_items_header = len(result["data"])
        return total_items_header

    # TODO: REVIEW: Unify with connector_extension_woocommerce
    def _exec_get(self, resource, *args, **kwargs):
        if resource == "system_status":
            return self._exec_wp_call(
                "get",
                resource,
                auth=(
                    self.backend_record.consumer_key,
                    self.backend_record.consumer_secret,
                ),
                verify=self.backend_record.verify_ssl,
                *args,
                **kwargs
            )
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
            res = self._exec_wp_call(
                "get",
                resource,
                params=params,
                auth=(
                    self.backend_record.consumer_key,
                    self.backend_record.consumer_secret,
                ),
                verify=self.backend_record.verify_ssl,
                *args,
                **kwargs
            )
            # WooCommerce returns a dict if the response is a single item
            if not isinstance(res["data"], list):
                res["data"] = [res["data"]]
            data += res["data"]
            params["offset"] += len(res["data"])
        return self._filter(data, common_domain)

    def _exec_post(self, resource, *args, **kwargs):
        auth = (self.backend_record.consumer_key, self.backend_record.consumer_secret)
        if "wordpress_backend_id" in self.backend_record:
            backend = self.backend_record.wordpress_backend_id
            auth = (backend.consumer_key, backend.consumer_secret)
        data_aux = kwargs.pop("data", {})
        headers = data_aux.pop("headers", {})
        data = data_aux.pop("data", {})
        res = self._exec_wp_call(
            "post",
            resource,
            data=data,
            headers=headers,
            auth=auth,
            verify=self.backend_record.verify_ssl,
        )

        return res["data"]

    def _exec_put(self, resource, *args, **kwargs):
        url = self.backend_record.url + "/wp-json/wp/v2/" + resource
        return self._exec_wp_call(
            "put", url=url, verify=self.backend_record.verify_ssl, *args, **kwargs
        )

    def _exec_delete(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def _exec_options(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def get_version(self):
        settings = self._exec("get", "settings")
        if settings and settings[0].get("title"):
            return "Wordpress '%s' connected" % settings[0].get("title")
        else:
            raise ValidationError(_("Wordpress not connected"))
