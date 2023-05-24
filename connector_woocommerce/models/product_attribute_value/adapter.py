# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component


class ValidatonError:
    pass


class WooCommerceProductAttributeValue(Component):
    _name = "woocommerce.product.attribute.value"
    _inherit = "woocommerce.adapter"

    _apply_on = "woocommerce.product.attribute.value"

    def read(self, external_id):  # pylint: disable=W8106
        external_id = self.binder_for().id2dict(external_id, in_field=False)
        url = "products/attributes/%s/terms/%s" % (
            external_id["parent_id"],
            external_id["id"],
        )
        return self._exec("get", url)

    # En el read no le pasamos un domain para que haga un filter, eso nos obliga a
    # hacerlo al final del search read del adapter de cada modelo.
    # Esto deberia ser mas generico y que el propio search read se encargara
    # de hacer esta faena?
    # El problema es que si al read le pasamos el domain hara la misma faena que el search read.
    # pero no veo logico que la faena del filtraje se deba duplicar en todos
    # los adapters de cada modelo.
    # Seria posible filtrar esto despues de hacer el read en el search read?
    # porque es una falta que tiene el read,
    # aunque este read no deberiamos filtrarlo, creo, es el producto tal cual.

    def search_read(self, domain=None):
        binder = self.binder_for()
        domain_dict = self._domain_to_normalized_dict(domain)
        external_id_fields = binder.get_id_fields(in_field=False)
        _, common_domain = self._extract_domain_clauses(domain, external_id_fields)
        external_id = binder.dict2id(domain_dict, in_field=False)
        if external_id:
            res = self.read(external_id)
        else:
            # We have parent id but not the woocommerce attribute value id
            if "parent_id" in domain_dict:
                _, common_domain = self._extract_domain_clauses(
                    common_domain, "parent_name"
                )
                url = "products/attributes/%s/terms" % domain_dict["parent_id"]
                res = self._exec("get", url, domain=common_domain)
                if res:
                    res[0]["parent_id"] = domain_dict["parent_id"]
            elif "parent_name" in domain_dict:
                partner_name, common_domain = self._extract_domain_clauses(
                    common_domain, ["parent_name"]
                )
                url = "products/attributes"
                res = self._exec(
                    "get", url, domain=[("name", "=", domain_dict["parent_name"])]
                )
                if not res:
                    return []
                if len(res) != 1:
                    raise ValidationError(_("More than one product parent found"))
                parent_id = res[0]["id"]
                url = "products/attributes/%s/terms" % parent_id
                res = self._exec("get", url, domain=common_domain)
                for elem in res:
                    elem["parent_id"] = parent_id
            else:
                return []
        return res

    def create(self, data):  # pylint: disable=W8106
        # # TODO: Esto devuelve una lista y nos va mal al hacer el dict2id
        if "parent_id" not in data:
            raise ValidationError(
                _("Attribute id is required to create attribute value on woocommerce.")
            )
        res = self._exec(
            "post",
            "products/attributes/%s/terms" % data["parent_id"],
            data=data,
        )
        if res:
            res.update({"parent_id": data["parent_id"]})
        return res

    # TODO: veure per que entra al write si ja troba binding
    def write(self, external_id, data):  # pylint: disable=W8106
        url_l = [
            "products/attributes/%s/terms" % data.pop("parent_id"),
            str(external_id),
        ]
        return self._exec("put", "/".join(url_l), data=data)

    def _get_filters_values(self):
        res = super()._get_filters_values()
        res.append("slug")
        return res
