# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import models
from odoo.http import request

from odoo.addons.base_rest.controllers.main import RestController

_logger = logging.getLogger(__name__)


class StockRestController(RestController):
    _root_path = "/api/v2/"
    _collection_name = "stock.rest.services"
    _default_auth = "user"

    def _process_method(
        self, service_name, method_name, *args, collection=None, params=None
    ):
        self._validate_method_name(method_name)
        if isinstance(collection, models.Model) and not collection:
            raise request.not_found()
        with self.service_component(service_name, collection=collection) as service:
            result = service.dispatch(method_name, *args, params=params)
            if "rows" in result:
                result = result["rows"]
            return self.make_response(result)
