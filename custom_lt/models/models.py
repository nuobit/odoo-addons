from openerp import models, fields, api, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    ref_as_supplier = fields.Char(string="Reference as a supplier", help="Reference used by the partner to identifiy us as his supplier")



