# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dev1@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.modules.module import load_information_from_description_file
from odoo.tools import convert_file


def update_module_data(env, module):
    """Load the data files of the module the way an update of the module does."""
    idref = {}
    for filename in load_information_from_description_file(module)["data"]:
        convert_file(env.cr, module, filename, idref, "update", False, "data")
