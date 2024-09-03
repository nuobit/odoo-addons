# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    wordpress_bind_ids = fields.One2many(
        comodel_name="wordpress.ir.attachment",
        inverse_name="odoo_id",
        string="WordPress Bindings",
    )

    # TODO:REVIEW: We can move this method to another module
    def _get_seo_meta_data(self):
        self.ensure_one()
        model_obj = self.env[self.res_model].browse(self.res_id)
        if hasattr(model_obj, "_get_seo_meta_data"):
            meta_data = model_obj._get_seo_meta_data()
            if not isinstance(meta_data, dict):
                raise ValidationError(_("it should always return a dictionary"))
            return meta_data
        else:
            return {}
