# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class LengowSaleOrderTypeAdapter(Component):
    _inherit = "lengow.sale.order.adapter"

    def search_read(self, domain):
        analize_data = None
        new_domain = []
        for e in domain:
            if e[0] == 'analize_data':
                analize_data = e[1]
            else:
                new_domain.append(e)
        res = super().search_read(new_domain)
        if analize_data:
            with open("connector_lengow_debug.csv", "a") as f:
                if not res:
                    line = [
                        analize_data['now'].isoformat(),
                        analize_data['since_date'].isoformat(),
                        '',
                        '',
                        '',
                        '',
                        '',
                        '',
                    ]
                    f.write(','.join(line) + '\n')
                else:
                    for ord in res:
                        line = [
                            analize_data['now'].isoformat(),
                            analize_data['since_date'].isoformat(),
                            ord['marketplace'],
                            ord['marketplace_order_id'],
                            ord['imported_at'].isoformat(),
                            ord['updated_at'].isoformat(),
                            ord['order_meta']['checksum'],
                            ord['lengow_status'],
                        ]
                        f.write(','.join(line) + '\n')
        return res
