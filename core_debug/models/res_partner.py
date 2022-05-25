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
        if not isinstance(other, models.BaseModel):
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
