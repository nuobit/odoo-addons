# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class SaleOrderImportMapChild(Component):
    _name = "oxigesti.sale.order.map.child.import"
    _inherit = "oxigesti.map.child.import"

    _apply_on = "oxigesti.sale.order.line"

    def get_item_values(self, map_record, to_attr, options):
        """Get the raw values from the child Mappers for the items.

        It can be overridden for instance to:

        * Change options
        * Use a :py:class:`~connector.connector.Binder` to know if an
          item already exists to modify an existing item, rather than to
          add it

        :param map_record: record that we are converting
        :type map_record: :py:class:`MapRecord`
        :param to_attr: destination field (can be used for introspecting
                        the relation)
        :type to_attr: str
        :param options: dict of options, herited from the main mapper

        """
        key = ["Codigo_Servicio", "CodigoArticulo", "Partida"]
        external_id = tuple([map_record.source[x] for x in key])

        binder = self.binder_for("oxigesti.sale.order.line")
        oxigesti_order_line = binder.to_internal(external_id, unwrap=False)

        if oxigesti_order_line:
            map_record.update(id=oxigesti_order_line.id)

        return map_record.values(**options)

    def format_items(self, items_values):
        """Format the values of the items mapped from the child Mappers.

        It can be overridden for instance to add the OpenERP
        relationships commands ``(6, 0, [IDs])``, ...

        As instance, it can be modified to handle update of existing
        items: check if an 'id' has been defined by
        :py:meth:`get_item_values` then use the ``(1, ID, {values}``)
        command

        :param items_values: list of values for the items to create
        :type items_values: list

        """
        ops = []
        for values in items_values:
            id = values.pop("id", None)
            if id:
                ops.append((1, id, values))
            else:
                ops.append((0, False, values))

        return ops


class SaleOrderImportMapper(Component):
    _name = "oxigesti.sale.order.import.mapper"
    _inherit = "oxigesti.import.mapper"

    _apply_on = "oxigesti.sale.order"

    def _get_order_lines(self, record, model_name):
        adapter = self.component(usage="backend.adapter", model_name=model_name)
        lines = adapter.search(
            filters=[
                ("Codigo_Servicio", "=", record["Codigo_Servicio"]),
            ]
        )

        return lines

    children = [
        (_get_order_lines, "oxigesti_order_line_ids", "oxigesti.sale.order.line")
    ]

    def _map_child(self, map_record, from_attr, to_attr, model_name):
        assert self._map_child_usage is not None, "_map_child_usage required"

        source = map_record.source
        if callable(from_attr):
            child_records = from_attr(self, source, model_name)
        else:
            child_records = source[from_attr]

        adapter = self.component(usage="backend.adapter", model_name=model_name)

        children = []
        for child_record in child_records:
            detail_record = adapter.read(child_record)
            mapper = self._get_map_child_component(model_name)
            items = mapper.get_items(
                [detail_record], map_record, to_attr, options=self.options
            )
            children.extend(items)

        return children

    @only_create
    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

    @only_create
    @mapping
    def company_id(self, record):
        return {"company_id": self.backend_record.company_id.id}

    @only_create
    @mapping
    def partner(self, record):
        external_id = (record["Codigo_Mutua"],)

        binder = self.binder_for("oxigesti.res.partner")
        partner = binder.to_internal(external_id, unwrap=True)
        assert partner, (
            "partner_id %s should have been imported in "
            "SaleOrderImporter._import_dependencies" % (external_id,)
        )

        return {"partner_id": partner.id}

    @only_create
    @mapping
    def order_date(self, record):
        return {
            "date_order": record["Fecha_Servicio"],
            "confirmation_date": record["Fecha_Servicio"],
            "validity_date": record["Fecha_Servicio"],
        }

    @only_create
    @mapping
    def team_id(self, record):
        return {"team_id": None}

    @only_create
    @mapping
    def user_id(self, record):
        return {"user_id": None}

    @only_create
    @mapping
    def service_number(self, record):
        if record["Codigo_Servicio"]:
            return {"service_number": record["Codigo_Servicio"]}

    @only_create
    @mapping
    def client_order(self, record):
        referencia_de_la_mutua = record["Referencia_de_la_Mutua"]
        if referencia_de_la_mutua and referencia_de_la_mutua.strip():
            return {"client_order_ref": referencia_de_la_mutua.strip()}

    @only_create
    @mapping
    def warehouse_id(self, record):
        if self.backend_record.warehouse_id:
            return {"warehouse_id": self.backend_record.warehouse_id.id}
