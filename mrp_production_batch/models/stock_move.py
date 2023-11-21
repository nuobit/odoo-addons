# # # Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# # # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
# from odoo import _, fields, models
# from odoo.exceptions import ValidationError
#
#
# class StockMove(models.Model):
#     _inherit = "stock.move"
#
#     production_batch_id = fields.Many2one(
#         comodel_name="mrp.production.batch",
#         string="Batch Production",
#         readonly=True,
#         ondelete="restrict",
#     )
#
#     def mrp_production_batch_create_wizard_action(self):
#         model = self.env.context.get("active_model")
#         mrp_productions = self.env[model].browse(self.env.context.get("active_ids"))
#         if not mrp_productions:
#             raise ValidationError(_("No productions selected"))
#         self.env["mrp.production.batch"].create(
#             {
#                 "creation_date": str(fields.Datetime.now()),
#                 "production_ids": [
#                     (6, 0, mrp_productions.ids),
#                 ],
#             }
#         )
