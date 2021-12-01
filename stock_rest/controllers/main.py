# Copyright 2021 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.base_rest.controllers import main


class StockRestController(main.RestController):
    _root_path = "/api/v2/"
    _collection_name = "stock.rest.services"
    _default_auth = "user"

    def _process_method(self, service_name, method_name, _id=None, params=None):
        self._validate_method_name(method_name)
        with self.service_component(service_name) as service:
            result = service.dispatch(method_name, _id, params)
            if 'rows' in result:
                result = result['rows']
            return self.make_response(result)
