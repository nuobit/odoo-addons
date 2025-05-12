# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools import check_barcode_encoding
from odoo.tools.safe_eval import safe_eval


class ReportBarcodeLabelTemplate(models.AbstractModel):
    _name = "report.barcode_label_template.report_label_template"
    _description = "Barcode Label Template Report"
    _inherit = "report.barcodes_gs1_label.report_gs1_barcode"

    def _prepare_report_label_template_data(self, data, lot, temp_config):
        data.update(
            {
                "position_x": temp_config.position_x,
                "position_y": temp_config.position_y,
                "width": temp_config.width,
            }
        )

        fields_data = []
        for field in temp_config.configuration_field_ids:
            field_name = field.field_id.name
            if lot.product_id.tracking == "lot":
                if field_name == "ref":
                    field_name = "name"
                elif field_name == "name":
                    field_name = False
            field_value = False
            if field_name:
                try:
                    expression = f"lot.{field_name}"
                    field_value = safe_eval(expression, globals_dict={"lot": lot})
                    if field_value and field.target_field:
                        expression = f"{expression}.{field.target_field}"
                        field_value = safe_eval(expression, globals_dict={"lot": lot})
                except Exception as error:
                    raise ValidationError(
                        _(
                            "Error in the barcode label template configuration while "
                            "evaluating expression: field [%(field)s] + target "
                            "field [%(target_field)s]"
                            "\nERROR:\n%(error)s\n\n"
                            "Please check the expression in the field configuration "
                            "and assign a valid expression. "
                            "This expression is not valid.\nExpression: %(expression)s"
                        )
                        % {
                            "field": field.field_id.field_description,
                            "target_field": field.target_field,
                            "error": error,
                            "expression": expression,
                        }
                    ) from error
            fields_data.append(
                {
                    "value": field_value,
                    "position_x": field.position_x,
                    "position_y": field.position_y,
                    "width": field.width,
                }
            )
        return {
            "barcodes_data": data,
            "fields_data": fields_data,
        }

    def _get_report_values(self, docids, data=None):
        temp_config_id = self.env.context.get("template_configuration_id")
        if not temp_config_id:
            raise ValidationError(_("No template configuration selected"))
        temp_config = (
            self.env["barcode.label.template.configuration"]
            .browse(temp_config_id)
            .exists()
        )
        lots = []
        for active_id in data["active_ids"]:
            lot = self.env["stock.lot"].browse(active_id).exists()
            if data["barcode_type"] == "gs1-datamatrix":
                data["barcode_values"] = self._prepare_gs1_values(lot.product_id, lot)
                data["barcode_string"] = self._get_gs1_barcode_string(
                    data["barcode_values"], data["barcode_type"]
                )
            elif data["barcode_type"] == "EAN13":
                product_barcode = lot.product_id.barcode or None
                if product_barcode and not check_barcode_encoding(
                    product_barcode, data["barcode_type"]
                ):
                    raise ValidationError(
                        _(
                            "Barcode {barcode} of product {product_name} "
                            "not valid for type {barcode_type}".format(
                                barcode=product_barcode,
                                product_name=lot.product_id.name,
                                barcode_type=data["barcode_type"],
                            )
                        )
                    )
                data["barcode_values"] = data["barcode_string"] = product_barcode
            else:
                raise ValidationError(
                    _(
                        "Barcode type [%s] not supported for this report"
                        % data["barcode_type"]
                    )
                )
            lots.append(
                self._prepare_report_label_template_data(data, lot, temp_config)
            )
        return {"lots": lots}
