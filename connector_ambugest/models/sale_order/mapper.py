# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from datetime import datetime

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class SaleOrderImportMapChild(Component):
    _name = "ambugest.sale.order.map.child.import"
    _inherit = "ambugest.map.child.import"
    _apply_on = "ambugest.sale.order.line"

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
        key = [
            "EMPRESA",
            "Fecha_Servicio",
            "Codigo_Servicio",
            "Servicio_Dia",
            "Servicio_Ano",
            "Articulo",
        ]
        external_id = tuple([map_record.source[x] for x in key])

        binder = self.binder_for("ambugest.sale.order.line")
        ambugest_order_line = binder.to_internal(external_id, unwrap=False)

        if ambugest_order_line:
            map_record.update(id=ambugest_order_line.id)

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
            _id = values.pop("id", None)
            if _id:
                ops.append((1, _id, values))
            else:
                ops.append((0, False, values))

        return ops


def nullif(field):
    def modifier(self, record, to_attr):
        value = record[field]
        return value and value.strip() or None

    return modifier


class SaleOrderImportMapper(Component):
    _name = "ambugest.sale.order.import.mapper"
    _inherit = "ambugest.import.mapper"
    _apply_on = "ambugest.sale.order"

    direct = [
        ("EMPRESA", "ambugest_empresa"),
        ("CodiUP", "ambugest_codiup"),
        ("Fecha_Servicio", "ambugest_fecha_servicio"),
        ("Codigo_Servicio", "ambugest_codigo_servicio"),
        ("Servicio_Dia", "ambugest_servicio_dia"),
        ("Servicio_Ano", "ambugest_servicio_ano"),
        (nullif("Num_Contrato"), "contract_number"),
        (nullif("Nombre_Asegurado"), "insured_name"),
        (nullif("DNI_Asegurado"), "insured_ident_cardnum"),
        (nullif("Num_Asegurado"), "policy_number"),
        (nullif("Referencia_autorizacion"), "auth_number"),
        (nullif("Matricula"), "plate_number"),
        ("Servicio_Ano", "service_number"),
        (nullif("Origen"), "origin"),
        (nullif("Destino"), "destination"),
        ("Clave", "service_key"),
        ("Motivo_Traslado", "service_transfer_reason"),
        ("Codigo_Aseguradora", "service_insurer_code"),
        (nullif("Nombre_Aseguradora"), "service_insurer_name"),
    ]

    @only_create
    @mapping
    def service_date(self, record):
        service_datetime = self.backend_record.tz_to_utc(
            datetime(
                year=record["Fecha_Servicio"].year,
                month=record["Fecha_Servicio"].month,
                day=record["Fecha_Servicio"].day,
                hour=record["Hora_Servicio"].hour,
                minute=record["Hora_Servicio"].minute,
                second=record["Hora_Servicio"].second,
            )
        )
        return {"service_date": service_datetime}

    def _get_order_lines(self, record, model_name):
        adapter = self.component(usage="backend.adapter", model_name=model_name)
        lines = adapter.search(
            filters={
                "EMPRESA": record["EMPRESA"],
                "Fecha_Servicio": record["Fecha_Servicio"],
                "Codigo_Servicio": record["Codigo_Servicio"],
                "Servicio_Dia": record["Servicio_Dia"],
                "Servicio_Ano": record["Servicio_Ano"],
            }
        )

        return lines

    children = [
        (_get_order_lines, "ambugest_order_line_ids", "ambugest.sale.order.line")
    ]

    def _map_child(self, map_record, from_attr, to_attr, model_name):
        assert self._map_child_usage is not None, "_map_child_usage required"

        source = map_record.source
        # TODO patch ImportMapper in connector to support callable
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
        external_id = (record["EMPRESA"], record["CodiUP"])

        binder = self.binder_for("ambugest.res.partner")
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
    def client_order(self, record):
        if record["Servicio_Ano"]:
            servicio_ano_str = str(record["Servicio_Ano"]).strip()
            if servicio_ano_str:
                return {"client_order_ref": servicio_ano_str}

    @only_create
    @mapping
    def service_direction(self, record):
        values = {
            "return_service": bool(record["Servicio_de_vuelta"]),
        }
        if record["Codigo_Ida_y_Vuelta"]:
            values.update(
                {
                    "round_trip_code": record["Codigo_Ida_y_Vuelta"],
                }
            )

        return values
