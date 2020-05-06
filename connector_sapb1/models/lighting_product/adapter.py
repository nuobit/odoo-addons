# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component


class LightingProductAdapter(Component):
    _name = 'sapb1.lighting.product.adapter'
    _inherit = 'sapb1.adapter'

    _apply_on = 'sapb1.lighting.product'

    _sql_search = r""""""

    _sql_read = r"""WITH
                    -- main tables with datetime
                    opor_updatetime AS (
                        SELECT c."DocEntry",
                               to_varchar(COALESCE(to_date(c."UpdateDate"), TO_DATE('1900-12-31',
                                                   'YYYY-MM-DD'))) AS "UpdateDate_str",
                               COALESCE(REPLACE_REGEXPR('([0-9]{2})([0-9]{2})([0-9]{2})' 
                                                        IN lpad(to_varchar(c."UpdateTS"), 6, '0')
                                                        WITH '\1:\2:\3'), '00:00:00') AS "UpdateTS_str"
                        FROM %(schema)s.OPOR c
                    ),
                    opor_base AS (
                        SELECT c.*,
                               to_timestamp(concat(u."UpdateDate_str", concat(' ', u."UpdateTS_str")),
                                           'YYYY-MM-DD HH24:MI:SS') AS "UpdateDateTime"
                        FROM opor_updatetime u, %(schema)s.OPOR c
                        WHERE u."DocEntry" = c."DocEntry"
                    ),
                    oitm_updatetime AS (
                        SELECT u."ItemCode",
                               to_varchar(COALESCE(to_date(u."UpdateDate"), TO_DATE('1900-12-31',
                                                   'YYYY-MM-DD'))) AS "UpdateDate_str",
                               COALESCE(REPLACE_REGEXPR('([0-9]{2})([0-9]{2})([0-9]{2})'
                                                        IN lpad(to_varchar(u."UpdateTS"), 6, '0')
                                                        WITH '\1:\2:\3'), '00:00:00') AS "UpdateTS_str"
                        FROM %(schema)s.OITM u
                    ),
                    oitm_base AS (
                        SELECT p.*,
                               to_timestamp(concat(u."UpdateDate_str", concat(' ', u."UpdateTS_str")),
                                           'YYYY-MM-DD HH24:MI:SS') AS "UpdateDateTime"
                        FROM oitm_updatetime u, %(schema)s.OITM p
                        WHERE u."ItemCode" = p."ItemCode" AND
                              u."ItemCode" NOT LIKE_REGEXPR '^.+\..+$' AND
                              p."U_ACC_Obsmark" IN ('Novedades', 'Catalogado', 'Descatalogado',
                                                    'Fe Digital', 'Histórico') and
                              COALESCE(p."U_U_especiales", 'N') = 'N' AND
                              p."ItmsGrpCod" IN (107, 108, 109, 111, 110) -- Cristher, Dopo, Exo, Indeluz, Accesorios
                    ),
                    -- purchase pricelist
                    purchase_price1 AS (
                        SELECT pl."ItemCode", pl."PriceList", pl."Price", NULLIF(trim(pl."Currency"),'') AS "Currency"
                        FROM %(schema)s.ITM1 pl
                        WHERE pl."PriceList" IN (12, 13) AND
                              pl."Price"!=0 AND NULLIF(trim(pl."Currency"),'') IS NOT NULL
                    ),
                    purchase_price AS (
                        SELECT p."ItemCode", p."Price" AS "PurchasePrice", p."Currency" AS "PurchasePriceCurrency"
                        FROM purchase_price1 p
                        WHERE NOT EXISTS (
                                SELECT p0.*
                                FROM purchase_price1 p0
                                WHERE p0."ItemCode" = p."ItemCode" AND
                                      p0."PriceList" < p."PriceList"
                            )
                    ),
                    -- future stock
                    pending_base AS (
                        SELECT lc."ItemCode",
                               sum(lc."OpenCreQty") AS "OnOrder",
                               max(c."UpdateDateTime") AS "UpdateDateTime",
                               lc."ShipDate" AS "ShipDate"
                        FROM %(schema)s.POR1 lc, opor_base c
                        WHERE lc."DocEntry" = c."DocEntry" AND
                              lc."WhsCode" = '00' AND
                              lc."OpenCreQty" != 0 AND
                              c.CANCELED = 'N'
                        GROUP BY lc."ItemCode", lc."ShipDate"
                        UNION ALL
                        SELECT o."ItemCode",
                               sum(o."PlannedQty" - (o."CmpltQty" + o."RjctQty")) AS "OnOrder",
                               max(o."UpdateDate") AS "UpdateDateTime",
                               o."DueDate" AS "ShipDate"
                        FROM %(schema)s.OWOR o
                        WHERE o."Warehouse" = '00' AND
                              o."Status" IN ('R', 'P') AND
                              (o."PlannedQty" - (o."CmpltQty" + o."RjctQty")) > 0
                        GROUP BY o."ItemCode", o."DueDate"
                    ),
                    pending_merged AS (
                        SELECT p."ItemCode",
                               sum(p."OnOrder") AS "OnOrder",
                               max(p."UpdateDateTime") AS "UpdateDateTime",
                               p."ShipDate" AS "ShipDate"
                        FROM pending_base p
                        GROUP BY p."ItemCode", p."ShipDate"
                    ),
                    stock_future AS (
                        SELECT p."ItemCode",
                               sum(p."OnOrder") AS "OnOrder",
                               max(p."ShipDate") AS "ShipDate",
                               max(p."UpdateDateTime") AS "UpdateDateTime"
                        FROM pending_merged p
                        GROUP BY p."ItemCode"
                    ),
                    -- current stock
                    stock_current AS (
                        SELECT pw."ItemCode",
                               pw."OnHand",
                               pw."IsCommited",
                               pw."WhsCode",
                               pw."updateDate" AS "UpdateDateTime"
                        FROM %(schema)s.OITW pw, %(schema)s.OITM p
                        WHERE pw."ItemCode" = p."ItemCode" AND
                              p."ItemType" = 'I' AND
                              p."InvntItem" = 'Y' AND
                              pw."WhsCode" = '00'
                    ),
                    -- current production orders
                    stock_capacity AS (
                        select lml."Father" AS "ItemCode",
                               min(round((ps."OnHand"- ps."IsCommited") / lml."Quantity",
                                             0, ROUND_DOWN)) AS "Capacity",
                               max(ps."UpdateDateTime") as "UpdateDateTime"
                        from %(schema)s.ITT1 lml, stock_current ps
                        WHERE lml."Code" = ps."ItemCode" AND
                              lml."Warehouse" = ps."WhsCode" AND
                              lml."Quantity" != 0
                        GROUP BY lml."Father"
                    ),
                    -- virtual stock
                    product_virtual_stock AS (
                        SELECT s."ItemCode",
                               0 AS "OnHand",
                               0 AS "IsCommited",
                               s."OnOrder",
                               s."ShipDate",
                               0 AS "Capacity",
                               s."UpdateDateTime"
                        FROM stock_future s
                        UNION ALL
                        SELECT s."ItemCode",
                               s."OnHand",
                               s."IsCommited",
                               0 AS "OnOrder",
                               NULL AS "ShipDate",
                               0 AS "Capacity",
                               s."UpdateDateTime"
                        FROM stock_current s
                        UNION ALL
                        SELECT s."ItemCode",
                               0 AS "OnHand",
                               0 AS "IsCommited",
                               0 AS "OnOrder",
                               NULL AS "ShipDate",
                               s."Capacity",
                               s."UpdateDateTime"
                        FROM stock_capacity s
                    ),
                    product_virtual_stock_all AS (
                        SELECT s."ItemCode",
                               sum(s."OnHand") AS "OnHand",
                               sum(s."IsCommited") AS "IsCommited",
                               sum(s."OnOrder") AS "OnOrder",
                               max(s."ShipDate") AS "ShipDate",
                               sum(s."Capacity") AS "Capacity",
                               max(s."UpdateDateTime") AS "UpdateDateTime"
                        FROM product_virtual_stock s
                        GROUP BY s."ItemCode"
                    ),
                    product as (
                        SELECT p."ItemCode", p."ItemName",
                               p."CodeBars",
                               g."ItmsGrpNam", p."U_U_familia", p."U_U_aplicacion",
                               p."U_ACC_Obsmark",
                               p."SWeight1", p."SVolume", p."SLength1", p."SWidth1", p."SHeight1",
                               s."OnHand",  s."IsCommited", s."OnOrder", s."ShipDate", s."Capacity",
                               p."AvgPrice", p."LastPurDat",
                               COALESCE(pp."PurchasePrice", 0) AS "PurchasePrice", pp."PurchasePriceCurrency",
                               COALESCE(t."Price", 0) as "Price", NULLIF(trim(t."Currency"),'') AS "Currency",
                               (CASE WHEN SECONDS_BETWEEN(s."UpdateDateTime", p."UpdateDateTime") > 0 THEN p."UpdateDateTime"
                                ELSE s."UpdateDateTime" END) AS "UpdateDateTime"
                        FROM product_virtual_stock_all s,
                             oitm_base p
                                LEFT JOIN %(schema)s.ITM1 t ON t."PriceList" = 11 AND p."ItemCode" = t."ItemCode"
                                LEFT JOIN purchase_price pp ON p."ItemCode" = pp."ItemCode",
                             %(schema)s.OITB g
                        WHERE s."ItemCode" = p."ItemCode" AND
                              p."ItmsGrpCod" = g."ItmsGrpCod"
                    )
                    select %(fields)s
                    from product
                    %(where)s
                 """

    _id = ('ItemCode',)
