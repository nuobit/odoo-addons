# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class AnphitrionBackendAdapter(Component):
    _name = "anphitrion.backend.adapter"
    _inherit = "anphitrion.adapter"

    _apply_on = "anphitrion.backend"

    def get_version(self):
        conn = self.conn()
        cr = conn.cursor()
        sql = "select @@version"
        cr.execute(sql)
        version = cr.fetchone()[0]
        cr.close()
        conn.close()
        return version
