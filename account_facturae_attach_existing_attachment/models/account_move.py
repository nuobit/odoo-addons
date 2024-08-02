# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import re
import xml.etree.ElementTree as ET

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


class AccountMove(models.Model):
    _inherit = "account.move"

    def _map_format_type_signed_facturaevx(self):
        return {
            "xlsx": "xls",
        }

    def get_format_types_facturaevx(self):
        xsd_file_path = get_module_resource(
            "l10n_es_facturae", "data", "Facturaev%s.xsd" % self.get_facturae_version()
        )
        tree = ET.parse(xsd_file_path)
        root = tree.getroot()
        namespaces = {"xs": "http://www.w3.org/2001/XMLSchema"}

        simple_type = root.find(
            ".//xs:simpleType[@name='AttachmentFormatType']", namespaces
        )
        if simple_type is not None:
            enumerations = simple_type.findall(".//xs:enumeration", namespaces)
            values = [enum.get("value") for enum in enumerations]
            return values
        else:
            raise ValidationError(
                _(
                    "SimpleType 'AttachmentFormatType' not found. Please contact your "
                    "system administrator."
                )
            )

    def _get_facturae_move_attachments(self):
        result = super()._get_facturae_move_attachments()
        if self.facturae and self.partner_id.attach_invoice_as_annex:
            move_attachments = self.env["ir.attachment"].search(
                [("res_id", "in", self.ids), ("res_model", "=", self._name)]
            )
            existing_checksums = {
                self.env["ir.attachment"]._compute_checksum(r["data"]) for r in result
            }
            for attachment in move_attachments:
                checksum = self.env["ir.attachment"]._compute_checksum(attachment.datas)
                if checksum not in existing_checksums:
                    match = re.match(r"^(.*)\.([^.]*)$", attachment.name)
                    if match:
                        description, content_type = match.groups()
                    else:
                        description = attachment.name
                        content_type = attachment.type

                    if self.env.context.get("facturae_signed", False):
                        content_type = self._map_format_type_signed_facturaevx().get(
                            content_type, content_type
                        )
                        if content_type not in self.get_format_types_facturaevx():
                            continue

                    result.append(
                        {
                            "data": attachment.datas,
                            "content_type": content_type,
                            "encoding": "BASE64",
                            "description": description,
                            "compression": False,
                        }
                    )
        return result
