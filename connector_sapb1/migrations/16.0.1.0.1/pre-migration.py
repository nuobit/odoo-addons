"""Pre-migration: claim auto-created queue.job.function records.

Existing installs may have queue.job.function records for export_record on
sapb1 binding models that were auto-created and have no ir_model_data entry
(thus no xml_id). When the new XML definition loads with noupdate="1",
Odoo would try to CREATE records with our new xml_ids, which fails due to
the (model_id, method) unique constraint.

Solution: insert the ir_model_data entries BEFORE the XML loads, so each
xml_id is already linked to the existing record. Also set allow_commit=True
directly (since noupdate="1" prevents the XML from updating fields).

See: https://github.com/OCA/queue/wiki/Upgrade-warning:-commits-inside-jobs
"""

JOB_FUNCTIONS = [
    ("sapb1_binding_method_export_record_job_function", "sapb1.binding"),
    ("sapb1_res_partner_export_record_job_function", "sapb1.res.partner"),
    ("sapb1_sale_order_export_record_job_function", "sapb1.sale.order"),
    ("sapb1_sale_order_line_export_record_job_function", "sapb1.sale.order.line"),
    ("sapb1_product_product_export_record_job_function", "sapb1.product.product"),
]


def migrate(cr, version):
    if not version:
        return
    for xml_id, model_name in JOB_FUNCTIONS:
        cr.execute(
            """
            SELECT qjf.id
            FROM queue_job_function qjf
            JOIN ir_model im ON im.id = qjf.model_id
            WHERE qjf.method = 'export_record' AND im.model = %s
            """,
            (model_name,),
        )
        row = cr.fetchone()
        if not row:
            continue
        qjf_id = row[0]
        cr.execute(
            """
            INSERT INTO ir_model_data
                (module, name, model, res_id, noupdate)
            VALUES
                ('connector_sapb1', %s, 'queue.job.function', %s, TRUE)
            ON CONFLICT (module, name) DO NOTHING
            """,
            (xml_id, qjf_id),
        )
        cr.execute(
            """
            UPDATE queue_job_function
            SET allow_commit = TRUE
            WHERE id = %s
            """,
            (qjf_id,),
        )
