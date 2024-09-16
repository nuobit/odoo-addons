# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WoocommerceWPMLBinding(models.AbstractModel):
    _name = "woocommerce.wpml.binding"
    _inherit = "connector.extension.external.binding"
    _description = "WooCommerce WPML Binding"

    backend_id = fields.Many2one(
        comodel_name="woocommerce.wpml.backend",
        string="WooCommerce WPML Backend",
        required=True,
        ondelete="restrict",
    )

    _sql_constraints = [
        (
            "woocommerce_internal_uniq",
            "unique(backend_id, odoo_id)",
            "A binding already exists with the same Internal (Odoo) ID.",
        ),
    ]

    @api.model
    def export_record(self, backend_record, relation, lang):
        """Export Odoo record"""
        with backend_record.work_on(self._name) as work:
            exporter = work.component(usage="record.direct.exporter")
            return exporter.run(relation, lang)

    # TODO: This resync_export is good for all models?
    #  Review Resync for Product Template WPML vs Product template
    def resync_export(self):
        for record in self:
            lang = self.env["res.lang"]._get_code_from_wpml_code(
                record.woocommerce_lang
            )
            if not lang:
                raise ValidationError(
                    _("Language not found with code %s") % record.woocommerce_lang
                )
            with record.backend_id.work_on(record._name) as work:
                binder = work.component(usage="binder")
                relation = binder.unwrap_binding(record).with_context(
                    resync_export=True
                )
            func = record.export_record
            if record.env.context.get("connector_delay"):
                func = func.with_delay
            func(record.backend_id, relation, lang)
        return True
