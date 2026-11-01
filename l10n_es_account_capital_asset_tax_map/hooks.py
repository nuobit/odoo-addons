# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


def _get_map_tax_data(chart_template):
    return chart_template._parse_csv(
        "es_common",
        "l10n.es.account.capital.asset.map.tax",
        module="l10n_es_account_capital_asset_tax_map",
    )


def post_init_hook(env):
    companies = env["res.company"].search(
        [
            ("chart_template", "like", "es_%"),
        ],
        order="parent_path",
    )
    for company in companies:
        ChartTemplate = env["account.chart.template"].with_company(company)
        map_tax_data_to_load = {}
        for xmlid, values in _get_map_tax_data(ChartTemplate).items():
            tax_src = ChartTemplate.ref(values["tax_src_id"], raise_if_not_found=False)
            tax_dest = ChartTemplate.ref(
                values["tax_dest_id"], raise_if_not_found=False
            )
            # A company without the taxes gets no row, and a row already
            # loaded with its chart template xml-id is left as it is
            if (
                tax_src
                and tax_dest
                and not ChartTemplate.ref(xmlid, raise_if_not_found=False)
            ):
                # The rows seeded up to 18.0.1.0.2 have no xml-id: the oldest
                # one of the pair takes it, instead of getting a duplicate
                map_tax = env["l10n.es.account.capital.asset.map.tax"].search(
                    [
                        ("company_id", "=", company.id),
                        ("tax_src_id", "=", tax_src.id),
                        ("tax_dest_id", "=", tax_dest.id),
                    ],
                    order="id",
                    limit=1,
                )
                if map_tax:
                    env["ir.model.data"]._update_xmlids(
                        [
                            {
                                "xml_id": f"account.{company.id}_{xmlid}",
                                "record": map_tax,
                                "noupdate": True,
                            }
                        ]
                    )
                else:
                    map_tax_data_to_load[xmlid] = values
        if map_tax_data_to_load:
            ChartTemplate._load_data(
                {"l10n.es.account.capital.asset.map.tax": map_tax_data_to_load}
            )
