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
                "position_x": temp_config.position_x
                / temp_config.correction_ratio_pxmm,
                "position_y": temp_config.position_y
                / temp_config.correction_ratio_pxmm,
                "width": temp_config.width / temp_config.correction_ratio_pxmm,
                "height": temp_config.height / temp_config.correction_ratio_pxmm,
                "humanreadable": temp_config.humanreadable or False,
                "resolution_width": temp_config.width
                / 25.4
                * temp_config.resolution_ppi,
                "resolution_height": temp_config.height
                / 25.4
                * temp_config.resolution_ppi,
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
                    "position_x": field.position_x / temp_config.correction_ratio_pxmm,
                    "position_y": field.position_y / temp_config.correction_ratio_pxmm,
                    "width": field.width / temp_config.correction_ratio_pxmm,
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
        barcode_data = {"barcode_type": temp_config.barcode_type}
        lots = []
        for active_id in data["active_ids"]:
            lot = self.env["stock.lot"].browse(active_id).exists()
            if barcode_data["barcode_type"] == "gs1-datamatrix":
                barcode_data["barcode_values"] = self._prepare_gs1_values(
                    {"product": lot.product_id, "lot": lot}
                )
                barcode_data["barcode_string"] = self._get_gs1_barcode_string(
                    barcode_data["barcode_values"], barcode_data["barcode_type"]
                )
            elif barcode_data["barcode_type"] == "EAN13":
                product_barcode = lot.product_id.barcode or None
                if (
                    product_barcode
                    and temp_config.check_barcode_encoding
                    and not check_barcode_encoding(
                        product_barcode, barcode_data["barcode_type"]
                    )
                ):
                    raise ValidationError(
                        _(
                            "Barcode [{barcode}] of product [{product_name}] "
                            "not valid for type [{barcode_type}]"
                        ).format(
                            barcode=product_barcode,
                            product_name=lot.product_id.name,
                            barcode_type=barcode_data["barcode_type"],
                        )
                    )
                barcode_data["barcode_values"] = barcode_data["barcode_string"] = (
                    product_barcode
                )
            else:
                raise ValidationError(
                    _("Barcode type [%s] not supported for this report")
                    % barcode_data["barcode_type"]
                )
            lots.append(
                self._prepare_report_label_template_data(barcode_data, lot, temp_config)
            )
        return {"lots": lots}
