# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = "stock.location"

    name = fields.Char(translate=True)

    @api.depends("name", "location_id.complete_name")
    def _compute_complete_name(self):
        # we set the method as in v11 where complete_name has the full path
        """ Forms complete name of location from parent location to child location. """
        for location in self:
            if location.location_id.complete_name:
                location.complete_name = "%s/%s" % (
                    location.location_id.complete_name,
                    location.name,
                )
            else:
                location.complete_name = location.name

    def name_get(self):
        # v11 method
        ret_list = []
        for location in self:
            orig_location = location
            name = location.name
            while location.location_id and location.usage != "view":
                location = location.location_id
                if not name:
                    raise UserError(_("You have to set a name for this location."))
                name = location.name + "/" + name
            ret_list.append((orig_location.id, name))
        return ret_list
