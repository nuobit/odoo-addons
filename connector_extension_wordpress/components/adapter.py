# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2023 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
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
        func = getattr(self, f"_exec_{op}")
        return func(resource, *args, **kwargs)

    def _manage_error_codes(
        self, op, res_data, res, resource, *args, raise_on_error=True, **kwargs
    ):
        if not res.ok:
            # WordPress answers an error with an object that holds its code
            # and its message
            if (
                isinstance(res_data, dict)
                and "code" in res_data
                and "message" in res_data
            ):
                if (
                    res.status_code == 404
                    and res_data["code"] == "rest_post_invalid_id"
                ):
                    error_message = _(
                        "Error: '%(message)s'. Probably the %(resource)s has been "
                        "removed from WordPress. "
                        "If it's the case, try to remove the binding of the %(model)s."
                    ) % {
                        "message": res_data["message"],
                        "resource": resource,
                        "model": self.model._name,
                    }
                elif (
                    res.status_code == 500
                    and res_data["code"] == "rest_upload_sideload_error"
                    # only POST and PUT upload a file
                    and op in ("post", "put")
                ):
                    headers = kwargs["headers"]
                    # an upload sent without headers, None or empty, has none
                    # to show
                    if headers:
                        error_message = _(
                            "WordPress refused the uploaded file: %(message)s "
                            "Check that WordPress accepts its format. "
                            "Request headers: %(headers)s"
                        ) % {
                            "message": res_data["message"],
                            "headers": ", ".join(
                                f"{name}: {value}" for name, value in headers.items()
                            ),
                        }
                    else:
                        error_message = _(
                            "WordPress refused the uploaded file: %(message)s "
                            "Check that WordPress accepts its format."
                        ) % {"message": res_data["message"]}
                else:
                    error_message = _(
                        "WordPress error %(code)s on %(resource)s: %(message)s"
                    ) % {
                        "code": res_data["code"],
                        "message": res_data["message"],
                        "resource": resource,
                    }
            else:
                error_message = _("WordPress error on %(resource)s: %(answer)s") % {
                    "resource": resource,
                    "answer": res.text,
                }
            if raise_on_error:
                raise ValidationError(error_message)
            return error_message
        return res_data

    def _exec_wp_call(self, op, resource, *args, **kwargs):
        backend = self._get_wordpress_backend()
        url = backend.url + "/wp-json/wp/v2/" + resource
        func = getattr(requests, op)
        try:
            res = func(
                url,
                *args,
                auth=(backend.username, backend.application_password),
                verify=backend.verify_ssl,
                **kwargs,
            )
            res_data = res.json()
            res_data = self._manage_error_codes(
                op, res_data, res, resource, *args, **kwargs
            )
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
                _("Error decoding json WordPress response: %(message)s\n%(response)s")
                % {
                    "message": e,
                    "response": res.text,
                }
            ) from e
        return result

    def _get_search_fields(self):
        return ["modified_after", "offset", "per_page", "page"]

    def get_total_items(self, resource, domain=None):
        if domain is None:
            domain = []
        filters_values = self._get_search_fields()
        real_domain, common_domain = self._extract_domain_clauses(
            domain, filters_values
        )
        params = self._domain_to_normalized_dict(real_domain)
        # TODO: make an optimization to get the total items and use the result
        params["per_page"] = 1
        result = self._exec_wp_call("get", resource, params=params)

        total_items_header = result["headers"]._store.get("x-wp-total")
        if total_items_header:
            total_items_header = int(total_items_header[1])
        else:
            data = result["data"]
            if not data:
                # an empty answer, whatever its JSON type
                total_items_header = 0
            elif isinstance(data, list):
                total_items_header = len(data)
            else:
                # WordPress returns a dict if the response is a single item
                total_items_header = 1
        return total_items_header

    # TODO: REVIEW: Unify with connector_extension_woocommerce
    def _exec_get(self, resource, *args, **kwargs):
        # an argument given as None is an argument not given
        for name in ("domain", "offset", "limit"):
            if name in kwargs and kwargs[name] is None:
                del kwargs[name]
        # WooCommerce has the parameter next on the response headers
        # to get the next page but we can't use it because if we use
        # the offset, the next page will have the same items as the first page.
        # It looks like a bug in WooCommerce API.
        domain = kwargs.pop("domain", [])
        search_fields = self._get_search_fields()
        real_domain, common_domain = self._extract_domain_clauses(domain, search_fields)
        params = self._domain_to_normalized_dict(real_domain)
        # An offset clause of the domain wins over the offset argument
        params.setdefault("offset", kwargs.pop("offset", 0))
        limit = kwargs.pop("limit", None)
        if limit is None:
            # WordPress counts every item of the query, whatever its offset
            limit = self.get_total_items(resource, domain) - params["offset"]
        # A per_page clause of the domain wins over the page size of the
        # backend the call reaches
        page_size = self._get_wordpress_backend().page_size
        per_page = params.setdefault("per_page", page_size if page_size > 0 else 100)
        data = []
        while len(data) < limit:
            if per_page > limit - len(data):
                params["per_page"] = limit - len(data)
            res = self._exec_wp_call("get", resource, *args, params=params, **kwargs)
            if not res["data"]:
                # Fewer items than expected: some were deleted after the
                # count, or the limit is above the total; an empty answer of
                # any JSON type
                break
            # WordPress returns a dict if the response is a single item
            if not isinstance(res["data"], list):
                res["data"] = [res["data"]]
            data += res["data"]
            params["offset"] += len(res["data"])
        return self._filter(data, common_domain)

    def _get_wordpress_backend(self):
        """The backend every call reaches, with its site, its credentials and
        its SSL check: the linked WordPress backend when one is set, else the
        backend itself."""
        backend = self.backend_record
        if "wordpress_backend_id" in backend and backend.wordpress_backend_id:
            backend = backend.wordpress_backend_id
        if "username" not in backend or "application_password" not in backend:
            raise ValidationError(
                _(
                    "The backend %(backend)s cannot call WordPress until a "
                    "WordPress backend is chosen on it."
                )
                % {"backend": backend.display_name}
            )
        return backend

    def _exec_post(self, resource, *args, **kwargs):
        data_aux = kwargs.pop("data", {})
        headers = data_aux.pop("headers", {})
        data = data_aux.pop("data", {})
        res = self._exec_wp_call(
            "post",
            resource,
            data=data,
            params=data_aux,
            headers=headers,
        )

        return res["data"]

    def _exec_put(self, resource, *args, **kwargs):
        data_aux = kwargs.pop("data", {})
        headers = data_aux.pop("headers", {})
        data = data_aux.pop("data", {})
        res = self._exec_wp_call(
            "put",
            resource,
            *args,
            data=data,
            params=data_aux,
            headers=headers,
            **kwargs,
        )
        return res["data"]

    def _exec_delete(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def _exec_options(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def get_version(self):
        settings = self._exec("get", "settings")
        if settings and settings[0].get("title"):
            return "Wordpress '{}' connected".format(settings[0].get("title"))
        else:
            raise ValidationError(_("Wordpress not connected"))
