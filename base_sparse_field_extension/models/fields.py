# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import json

from odoo import fields

from odoo.addons.base_sparse_field.models.fields import Serialized


class ExtendedSerialized(Serialized):
    def convert_to_cache(self, value, record, validate=True):
        return json.dumps(value) if isinstance(value, (list, dict)) else (value or None)


fields.ExtendedSerialized = ExtendedSerialized
