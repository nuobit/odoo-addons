# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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

    def _exec_wp_call(self, op, url, *args, **kwargs):
        func = getattr(requests, op)
        try:
            res = func(url, *args, **kwargs)
            data = res.json()
            if not res.ok:
                raise ValidationError(_("Error: %s") % data)
        except requests.exceptions.ConnectionError as e:
            raise RetryableJobError(_("Error connecting to WordPress: %s") % e) from e
        except json.JSONDecodeError as e:
            raise ValidationError(
                _("Error decoding json WordPress response: %s\n%s") % (e, res.text)
            ) from e
        return data

    def _exec_get(self, resource, *args, **kwargs):
        url = self.backend_record.url + "/wp-json/wp/v2/" + resource
        return self._exec_wp_call(
            "get",
            url=url,
            auth=(
                self.backend_record.consumer_key,
                self.backend_record.consumer_secret,
            ),
        )

    def _exec_post(self, resource, *args, **kwargs):
        auth = (self.backend_record.consumer_key, self.backend_record.consumer_secret)
        if "wordpress_backend_id" in self.backend_record:
            backend = self.backend_record.wordpress_backend_id
            auth = (backend.consumer_key, backend.consumer_secret)
        data_aux = kwargs.pop("data", {})
        headers = data_aux.pop("headers", {})
        data = data_aux.pop("data", {})
        checksum = False
        if data_aux.get("checksum"):
            checksum = data_aux.pop("checksum")
        url = self.backend_record.url + "/wp-json/wp/v2/" + resource
        result = self._exec_wp_call(
            "post", url=url, data=data, headers=headers, auth=auth
        )
        if checksum:
            result["checksum"] = checksum
        return result

    def _exec_put(self, resource, *args, **kwargs):
        url = self.backend_record.url + "/wp-json/wp/v2/" + resource
        return self._exec_wp_call("put", url=url, *args, **kwargs)

    def _exec_delete(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def _exec_options(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def get_version(self):
        settings = self._exec("get", "settings")
        if settings.get("title"):
            return "Wordpress '%s' connected" % settings.get("title")
        else:
            raise ValidationError(_("Wordpress not connected"))
