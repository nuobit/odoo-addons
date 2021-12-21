# Copyright 2021 NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ReportStockForecast(models.Model):
    _inherit = "report.stock.forecast"

    sale_order_id = fields.Many2one("sale.order", readonly=True)
    purchase_order_id = fields.Many2one("purchase.order", readonly=True)

    def init(self):
        super().init()
        self._cr.execute(
            """CREATE or REPLACE VIEW report_stock_forecast AS (select
        MIN(id) as id,
        product_id as product_id,
        to_char(date, 'YYYY-MM-DD') as date,
        sum(product_qty) as quantity,
        sum(sum(product_qty)) over (partition by product_id
    order by
        date) as cumulative_quantity,
        company_id,
        sale_order_id,
        purchase_order_id
    from
        (
        select
            MIN(id) as id,
            MAIN.product_id as product_id,
            SUB.date as date,
            case
                when MAIN.date = SUB.date then sum(MAIN.product_qty)
                else 0
            end as product_qty,
            MAIN.company_id as company_id,
            MAIN.sale_order_id as sale_order_id,
            MAIN.purchase_order_id as purchase_order_id
        from
            (
            select
                MIN(sq.id) as id,
                sq.product_id,
                date_trunc('week', to_date(to_char(CURRENT_DATE, 'YYYY/MM/DD'),
                'YYYY/MM/DD')) as date,
                SUM(sq.quantity) as product_qty,
                sq.company_id,
                NULL::int4 as sale_order_id,
                NULL::int4 as purchase_order_id
            from
                stock_quant as sq
            left join
                product_product on
                product_product.id = sq.product_id
            left join
                stock_location location_id on
                sq.location_id = location_id.id
            where
                location_id.usage = 'internal'
            group by
                date,
                sq.product_id,
                sq.company_id
        union all
            select
                MIN(-sm.id) as id,
                sm.product_id,
                case
                    when sm.date_expected > CURRENT_DATE
                        then date_trunc('week', to_date(to_char(sm.date_expected,
                         'YYYY/MM/DD'), 'YYYY/MM/DD'))
                    else date_trunc('week', to_date(to_char(CURRENT_DATE,
                    'YYYY/MM/DD'), 'YYYY/MM/DD'))
                end
                    as date,
                SUM(sm.product_qty) as product_qty,
                sm.company_id,
                null as sale_order_id,
                p_order_line.order_id as purchase_order_id
            from
                stock_move as sm
            left join
                   product_product on
                product_product.id = sm.product_id
            left join
                stock_location dest_location on
                sm.location_dest_id = dest_location.id
            left join
                stock_location source_location on
                sm.location_id = source_location.id
            left join
                   purchase_order_line p_order_line on
                sm.purchase_line_id = p_order_line.id
            where
                sm.state in
                ('confirmed', 'partially_available', 'assigned', 'waiting')
                and
                source_location.usage != 'internal'
                and dest_location.usage = 'internal'
            group by
                sm.date_expected,
                sm.product_id,
                sm.company_id,
                p_order_line.order_id
        union all
            select
                MIN(-sm.id) as id,
                sm.product_id,
                case
                    when sm.date_expected > CURRENT_DATE
                        then date_trunc('week', to_date(to_char(sm.date_expected,
                         'YYYY/MM/DD'), 'YYYY/MM/DD'))
                    else date_trunc('week', to_date(to_char(CURRENT_DATE,
                     'YYYY/MM/DD'), 'YYYY/MM/DD'))
                end
                    as date,
                SUM(-(sm.product_qty)) as product_qty,
                sm.company_id,
                s_order_line.order_id as sale_order_id,
                null as purchase_order_id
            from
                stock_move as sm
            left join
                   product_product on
                product_product.id = sm.product_id
            left join
                   stock_location source_location on
                sm.location_id = source_location.id
            left join
                   stock_location dest_location on
                sm.location_dest_id = dest_location.id
                            LEFT JOIN
                   sale_order_line s_order_line ON sm.sale_line_id = s_order_line.id
            where
                sm.state in
                ('confirmed', 'partially_available', 'assigned', 'waiting')
                and
                source_location.usage = 'internal'
                and dest_location.usage != 'internal'
            group by
                sm.date_expected,
                sm.product_id,
                sm.company_id,
                s_order_line.order_id
                )
             as MAIN
        left join
         (
            select
                distinct date
            from
                (
                select
                    date_trunc('week', CURRENT_DATE) as DATE
            union all
                select
                    date_trunc('week', to_date(to_char
                    (sm.date_expected, 'YYYY/MM/DD'),
                     'YYYY/MM/DD')) as date
                from
                    stock_move sm
                left join
                 stock_location source_location on
                    sm.location_id = source_location.id
                left join
                 stock_location dest_location on
                    sm.location_dest_id = dest_location.id
                where
                    sm.state in ('confirmed', 'assigned', 'waiting')
                        and sm.date_expected > CURRENT_DATE
                        and
                 ((dest_location.usage = 'internal'
                            and source_location.usage != 'internal')
                        or (source_location.usage = 'internal'
                            and dest_location.usage != 'internal'))) as DATE_SEARCH)
                 SUB on
            (SUB.date is not null)
        group by
            MAIN.product_id,
            SUB.date,
            MAIN.date,
            MAIN.company_id,
            MAIN.sale_order_id,
            MAIN.purchase_order_id
        ) as final
    group by
        product_id,
        date,
        company_id,
    sale_order_id,
        purchase_order_id)"""
        )
