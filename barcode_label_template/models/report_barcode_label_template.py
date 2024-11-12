# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class ReportBarcodeLabelTemplate(models.AbstractModel):
    _name = "report.barcode_label_template.report_label_template"
    _inherit = "report.barcodes_gs1_label.report_gs1_barcode"

    def _prepare_report_label_template_data(self, data, gs1_barcode, lot, temp_config):
        barcodes_data = {}
        if gs1_barcode:
            barcodes_data = {
                "product": lot.product_id,
                "type": data["barcode_type"],
                "values": gs1_barcode,
                "string": self._get_gs1_barcode_string(gs1_barcode, "gs1-datamatrix"),
                "position_x": temp_config.position_x,
                "position_y": temp_config.position_y,
                "width": temp_config.width,
            }
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
                    expression = "lot.{}".format(field_name)
                    field_value = safe_eval(expression, {"lot": lot})
                    if field_value and field.target_field:
                        expression = "{}.{}".format(expression, field.target_field)
                        field_value = safe_eval(expression, {"lot": lot})
                except Exception as error:
                    raise ValidationError(
                        _(
                            "Error in the barcode label template configuration while "
                            "evaluating expression: field [%s] + target field [%s]"
                            "\nERROR:\n%s\n\n"
                            "Please check the expression in the field configuration"
                            "and assign a valid expression. "
                            "This expression is not valid.\nExpression: %s"
                        )
                        % (
                            field.field_id.field_description,
                            field.target_field,
                            error,
                            expression,
                        )
                    )
            fields_data.append(
                {
                    "value": field_value,
                    "position_x": field.position_x,
                    "position_y": field.position_y,
                    "width": field.width,
                }
            )
        return {
            "barcodes_data": barcodes_data,
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
        datas = []
        for active_id in data["active_ids"]:
            lot = self.env["stock.production.lot"].browse(active_id).exists()
            gs1_barcode = self._prepare_gs1_values(lot.product_id, lot)
            datas.append(
                self._prepare_report_label_template_data(
                    data, gs1_barcode, lot, temp_config
                )
            )
        return {"datas": datas}
