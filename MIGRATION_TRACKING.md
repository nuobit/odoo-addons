# Seguimiento de Migración a la versión 18.0

Seguimiento del progreso de migración de todos los módulos de este repositorio a Odoo 18.0, basado en la [issue original #699](https://github.com/nuobit/odoo-addons/issues/699).

## Recursos y Documentación
- [Migration to version 12.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-12.0)
- [Migration to version 13.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-13.0)
- [Migration to version 14.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-14.0)
- [Migration to version 15.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-15.0)
- [Migration to version 16.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-16.0)
- [Migration to version 17.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-17.0)
- [Migration to version 18.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-18.0)

## Estadísticas del Progreso
- **Total de módulos**: 199
- **Módulos migrados**: 30 ✅
- **Módulos pendientes**: 169 ⏳
- **Progreso**: 15.08% completado

## Módulos Completados ✅
_Módulos que ya tienen PRs de migración creados_

- [x] account_asset_report_category - [#669](https://github.com/nuobit/odoo-addons/pull/669)
- [x] account_financial_report_number - [#672](https://github.com/nuobit/odoo-addons/pull/672)
- [x] account_invoice_attachment_required - [#650](https://github.com/nuobit/odoo-addons/pull/650)
- [x] account_invoice_mass_email - [#687](https://github.com/nuobit/odoo-addons/pull/687)
- [x] account_invoice_sent_flag - [#691](https://github.com/nuobit/odoo-addons/pull/691)
- [x] account_move_accrual_entry - [#697](https://github.com/nuobit/odoo-addons/pull/697)
- [x] barcode_label_template - [#644](https://github.com/nuobit/odoo-addons/pull/644)
- [x] barcodes_gs1_label - [#643](https://github.com/nuobit/odoo-addons/pull/643)
- [x] base_user_update_partner - [#671](https://github.com/nuobit/odoo-addons/pull/671)
- [x] connector_extension - [#663](https://github.com/nuobit/odoo-addons/pull/663)
- [x] connector_extension_mssql - [#666](https://github.com/nuobit/odoo-addons/pull/666)
- [x] connector_extension_mysql - [#665](https://github.com/nuobit/odoo-addons/pull/665)
- [x] connector_extension_sql - [#664](https://github.com/nuobit/odoo-addons/pull/664)
- [x] contract_comment - [#640](https://github.com/nuobit/odoo-addons/pull/640)
- [x] crm_lost_stage - [#655](https://github.com/nuobit/odoo-addons/pull/655)
- [x] display_name_mixin - [#637](https://github.com/nuobit/odoo-addons/pull/637)
- [x] l10n_es_facturae_cege - [#659](https://github.com/nuobit/odoo-addons/pull/659)
- [x] partner_default_journal - [#670](https://github.com/nuobit/odoo-addons/pull/670)
- [x] partner_firstname_swap_position - [#656](https://github.com/nuobit/odoo-addons/pull/656)
- [x] partner_lang_required - [#636](https://github.com/nuobit/odoo-addons/pull/636)
- [x] partner_name_reference - [#654](https://github.com/nuobit/odoo-addons/pull/654)
- [x] partner_name_vat - [#639](https://github.com/nuobit/odoo-addons/pull/639)
- [x] payroll_sage - [#690](https://github.com/nuobit/odoo-addons/pull/690)
- [x] product_supplier_search - [#692](https://github.com/nuobit/odoo-addons/pull/692)
- [x] project_legal_management - [#693](https://github.com/nuobit/odoo-addons/pull/693)
- [x] repair_order_default_location - [#696](https://github.com/nuobit/odoo-addons/pull/696)
- [x] res_lang_shortname - [#653](https://github.com/nuobit/odoo-addons/pull/653)
- [x] sale_order_invoiced_unlink - [#675](https://github.com/nuobit/odoo-addons/pull/675)
- [x] stock_picking_employee - [#657](https://github.com/nuobit/odoo-addons/pull/657)
- [x] stock_picking_import_serials - [#695](https://github.com/nuobit/odoo-addons/pull/695)

## Módulos Pendientes ⏳
_Módulos que aún necesitan migración_

### Módulos de Contabilidad
- [ ] account_asset_invoice_line_link
- [ ] account_asset_management_extension
- [ ] account_asset_non_deductible
- [ ] account_asset_tax_consistency
- [ ] account_asset_transfer_extension
- [ ] account_bank_statement_balance_start_protection
- [ ] account_cash_statement_restrict
- [ ] account_facturae_attach_existing_attachment
- [ ] account_financial_report_multi_company
- [ ] account_invoice_batches
- [ ] account_invoice_batches_accrual_entry
- [ ] account_invoice_hide_payment_button
- [ ] account_invoice_line_page_size
- [ ] account_invoice_name_short
- [ ] account_invoice_report_lot
- [ ] account_invoice_report_service
- [ ] account_invoice_report_service_facturae
- [ ] account_invoice_same_accounting_date
- [ ] account_invoice_same_accounting_date_prorate
- [ ] account_invoices_batches_mail_attach_existing_attachment
- [ ] account_mail_attach_existing_attachment
- [ ] account_move_asset_review
- [ ] account_move_service
- [ ] account_move_service_report_xlsx
- [ ] account_move_show_date_out_invoices
- [ ] account_payment_partner_sorted
- [ ] account_project_task_state
- [ ] account_template_view

### Módulos Base y Utilidades
- [ ] bank_multiple_acc_number
- [ ] barcodes_gs1_label_expiry
- [ ] base_report_gs1_barcode
- [ ] base_report_pdf_css_reset

### Conectores
- [ ] connector_ambugest
- [ ] connector_common
- [ ] connector_ertransit
- [ ] connector_lengow
- [ ] connector_oxigesti
- [ ] connector_sage
- [ ] connector_sapb1
- [ ] connector_veloconnect
- [ ] connector_veloconnect_fuchs_movesa

### Contratos
- [ ] contract_line_tax
- [ ] contract_mandate_default
- [ ] contract_manual_security
- [ ] contract_payment_mode_partner
- [ ] contract_sii

### Entrega y Logística
- [ ] delivery_mrw_no_info

### Localización España
- [ ] l10n_es_account_asset_tax_consistency
- [ ] l10n_es_account_asset_tax_consistency_prorate
- [ ] l10n_es_account_capital_asset
- [ ] l10n_es_account_capital_asset_tax_map
- [ ] l10n_es_account_capital_asset_tax_map_prorate
- [ ] l10n_es_account_menu
- [ ] l10n_es_account_statement_import_n43_company
- [ ] l10n_es_account_statement_import_n43_overlap
- [ ] l10n_es_aeat_mod303_special_prorate
- [ ] l10n_es_aeat_mod303_special_prorate_regularization
- [ ] l10n_es_aeat_mod303_special_prorate_regularization_capital_asset
- [ ] l10n_es_aeat_mod303_special_prorate_regularization_capital_asset_auc
- [ ] l10n_es_aeat_mod303_special_prorate_regularization_capital_asset_legacy
- [ ] l10n_es_aeat_mod303_special_prorate_regularization_prorate
- [ ] l10n_es_aeat_prorate_asset
- [ ] l10n_es_aeat_sii_oca_extension
- [ ] l10n_es_aeat_sii_oca_mock
- [ ] l10n_es_aeat_sii_oca_special_prorate
- [ ] l10n_es_aeat_sii_special_prorate_regularization_capital_asset
- [ ] l10n_es_aeat_sii_special_prorate_regularization_capital_asset_mock
- [ ] l10n_es_aeat_vat_special_prorrate
- [ ] l10n_es_aeat_vat_special_prorrate_purchase
- [ ] l10n_es_asset_extension
- [ ] l10n_es_banking_sepa_direct_debit_order_sabadell
- [ ] l10n_es_dua_special_prorrate
- [ ] l10n_es_extension
- [ ] l10n_es_facturae_auto_date
- [ ] l10n_es_facturae_default_bank_account
- [ ] l10n_es_facturae_service
- [ ] l10n_es_facturae_set_sent
- [ ] l10n_es_facturae_tax_rounding
- [ ] l10n_es_special_prorate

### Mantenimiento
- [ ] maintenance_request_date_editable

### Partners/Contactos
- [ ] partner_default_company
- [ ] partner_document
- [ ] partner_email_mobile_required
- [ ] partner_review

### Punto de Venta
- [ ] pos_product_pack
- [ ] pos_product_service_time
- [ ] pos_restaurant_note_print

### Listas de Precios
- [ ] pricelist_massive_update_contract

### Productos
- [ ] product_bike_info
- [ ] product_cost_hide
- [ ] product_expiry_removal_required
- [ ] product_image_removal_required
- [ ] product_multi_unique_barcode
- [ ] product_service_time
- [ ] product_supplier_ref
- [ ] product_supplierinfo_unique
- [ ] product_unique_barcode
- [ ] product_unique_internal_reference

### Proyectos
- [ ] project_category_parent_group
- [ ] project_task_alternate_name
- [ ] project_task_bike_location
- [ ] project_task_date_consistency
- [ ] project_task_hide_tasks
- [ ] project_task_metatype
- [ ] project_timeline_calendar
- [ ] project_timeline_default_view

### Compras
- [ ] purchase_order_new_line_uom
- [ ] purchase_stock_order_description
- [ ] purchase_stock_supplier_product_code

### Calidad
- [ ] quality_partner

### Reparaciones
- [ ] repair_employee

### Reportes
- [ ] report_json
- [ ] report_qweb_pdf_chunks

### Ventas
- [ ] sale_line_partner_description
- [ ] sale_order_bike_location
- [ ] sale_order_cancel_stock
- [ ] sale_order_date_show
- [ ] sale_order_invoice_date
- [ ] sale_order_invoicing_exclude
- [ ] sale_order_line_page_size
- [ ] sale_order_margin
- [ ] sale_order_service
- [ ] sale_order_task_autoassign
- [ ] sale_order_task_autoassign_pack
- [ ] sale_order_task_cancel
- [ ] sale_report_product_bike_info
- [ ] sale_report_product_type
- [ ] sale_specific_order_date

### Inventario y Stock
- [ ] stock_barcodes_gs1_extended
- [ ] stock_barcodes_option_new_scan
- [ ] stock_barcodes_qty_virtual_location
- [ ] stock_barcodes_serial_autoconfirm
- [ ] stock_barcodes_serial_source_relocation
- [ ] stock_barcodes_sku
- [ ] stock_barcodes_unique_field
- [ ] stock_inventory_additional_groups
- [ ] stock_location_code
- [ ] stock_location_flowable
- [ ] stock_location_localization_text
- [ ] stock_location_tag
- [ ] stock_move_line_picking
- [ ] stock_move_line_sale_order
- [ ] stock_move_no_merge
- [ ] stock_orderpoint_manual_procurement_zero
- [ ] stock_orderpoint_qty_restrict
- [ ] stock_orderpoint_sync_template
- [ ] stock_picking_date_filter
- [ ] stock_picking_default_product_search
- [ ] stock_picking_line_description
- [ ] stock_picking_line_location_order
- [ ] stock_picking_line_price
- [ ] stock_picking_partner_ref
- [ ] stock_picking_partner_ref_search
- [ ] stock_picking_report_delivery_note
- [ ] stock_picking_report_delivery_note_kit
- [ ] stock_picking_report_location_order
- [ ] stock_putaway_no_internal
- [ ] stock_putaway_no_internal_mrp
- [ ] stock_reordering_inmediate_transfer
- [ ] stock_rest
- [ ] stock_restrict_lot_name
- [ ] stock_tracking_integrity
- [ ] stock_unique_serial

### Herramientas
- [ ] tools_mimetypes_extension

### Web/UI
- [ ] web_line_page_size
- [ ] web_login_default_logo
- [ ] web_notebook_wrap

### Website
- [ ] website_erp_login
- [ ] website_erp_login_default_logo

---

## Instrucciones para Contribuir

1. **Elige un módulo** de la lista de pendientes
2. **Crea un PR** siguiendo el formato: `[18.0][MIG] nombre_del_modulo: Migration to 18.0`
3. **Actualiza esta issue** marcando el módulo como completado y añadiendo el enlace al PR
4. **Sigue las guías** de migración enlazadas arriba

## Notas
- Esta issue se actualiza automáticamente conforme se van creando nuevos PRs de migración
- Los PRs marcados con estados específicos (como "changes requested") pueden necesitar revisión adicional
- Algunos módulos pueden tener dependencias que requieren ser migradas primero

_Última actualización: Septiembre 2025_