# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging
from inspect import currentframe

from odoo import models
from odoo.tools.func import frame_codeinfo

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = "res.partner"

    def __eq__(self, other):
        """Test whether two recordsets are equivalent (up to reordering)."""
        if not isinstance(other, Partner):
            if other:
                filename, lineno = frame_codeinfo(currentframe(), 1)
                _logger.warning(
                    "Comparing apples and oranges: %r == %r (%s:%s)",
                    self,
                    other,
                    filename,
                    lineno,
                )
                raise Exception()
            return NotImplemented
        return self._name == other._name and set(self._ids) == set(other._ids)

    def address_get(self, adr_pref=None):
        """ Find contacts/addresses of the right type(s) by doing a depth-first-search
        through descendants within company boundaries (stop at entities flagged ``is_company``)
        then continuing the search at the ancestors that are within the same company boundaries.
        Defaults to partners of type ``'default'`` when the exact type is not found, or to the
        provided partner itself if no type ``'default'`` is found either. """
        adr_pref = set(adr_pref or [])
        if 'contact' not in adr_pref:
            adr_pref.add('contact')
        result = {}
        visited = self.env["res.partner"]
        for partner in self:
            current_partner = partner
            while current_partner:
                to_scan = [current_partner]
                # Scan descendants, DFS
                while to_scan:
                    record = to_scan.pop(0)
                    # _logger.info("ADDRESS_GET: record %s of type %s, visited %s", record, type(record), visited)
                    visited |= record
                    if record.type in adr_pref and not result.get(record.type):
                        result[record.type] = record.id
                    if len(result) == len(adr_pref):
                        return result
                    to_scan = [c for c in record.child_ids
                                 if c not in visited
                                 and not c.is_company] + to_scan

                # Continue scanning at ancestor if current_partner is not a commercial entity
                if current_partner.is_company or not current_partner.parent_id:
                    break
                current_partner = current_partner.parent_id

        # default to type 'contact' or the partner itself
        default = result.get('contact', self.id or False)
        for adr_type in adr_pref:
            result[adr_type] = result.get(adr_type) or default
        return result
