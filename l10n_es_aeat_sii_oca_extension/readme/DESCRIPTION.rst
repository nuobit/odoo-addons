This module extends the OCA SII (Suministro Inmediato de Información en el IVA) module with
additional functionalities and fixes that are not accepted or delayed by the OCA l10n_spain
localization community.

**All Features Provided:**

**1. CuotaDeducible Support (Partially Deductible Taxes)**

For Received Invoices (Vendor Bills):

* Automatically calculates the actual deductible amount of VAT based on tax configuration
* Only includes the portion that is truly deductible (based on tax repartition lines with account)
* Adds the CuotaDeducible field to SII submissions for received invoices
* Works for taxes mapped as SFRS (IVA Soportado) and SFRISP (IVA Inversión del Sujeto Pasivo)

How it works:

* Extends ``account.move.line`` to track actual deductible amounts during tax processing
* Automatically sums deductible portions based on tax repartition configuration
* No configuration needed - works automatically if tax has partial deductibility configured

**2. Clave "06" Support (Grupo de Entidades - Modalidad Avanzada)**

Problem Solved:

Companies using **ClaveRegimenEspecialOTrascendencia = "06"** (VAT group in advanced mode)
receive **SII Error 1234** when submitting invoices with both services and goods.

What the module does automatically:

* For Outgoing Invoices (Customer Invoices):

  * Merges services (PrestacionServicios) and goods (Entrega) into a single tax breakdown
  * Consolidates multiple tax lines with the same rate (TipoImpositivo) into one line
  * Transforms from DesgloseTipoOperacion to DesgloseFactura structure
  * Calculates and adds BaseImponibleACoste field automatically
  * Rounds BaseImponibleACoste to proper decimal precision

* For Incoming Invoices (Vendor Bills):

  * Calculates and adds BaseImponibleACoste field automatically
  * Ensures proper structure for AEAT validation

Result: SII submissions pass AEAT validation without Error 1234

**3. Extensible Tax Agency Hooks**

For Advanced Customizations:

* Provides hooks in ``aeat.tax.agency`` model to extend SII web service configurations
* Methods ``_prepare_sii_wdsl_mapping()`` and ``_prepare_sii_port_name_mapping()`` can be overridden
* Allows custom modules to add new WSDL endpoints or modify connection parameters
* Useful for specialized tax agency configurations or testing environments

**When to Use This Module:**

Install this module if you need:

* Partially deductible VAT reporting (CuotaDeducible field in received invoices)
* VAT group in advanced mode (modalidad avanzada) with clave "06"
* Fix for SII Error 1234 when submitting invoices with services + goods
* Custom tax agency configurations (extensibility hooks)

**How It Works:**

The module works automatically after installation:

* No configuration required for standard features
* Only activates clave "06" transformations when registration key = "06" is detected
* Doesn't affect other invoices - backwards compatible
* CuotaDeducible is calculated for all received invoices based on tax configuration
* All transformations happen transparently during SII submission

**Technical Details:**

Models Extended:

* ``account.move`` - Adds SII invoice processing for clave "06" and CuotaDeducible
* ``account.move.line`` - Tracks actual deductible amounts during tax processing
* ``aeat.tax.agency`` - Provides extensibility hooks for custom configurations

Key Methods:

* ``_get_sii_in_taxes_deductible()`` - Calculates deductible VAT amount
* ``_get_sii_out_taxes()`` - Transforms tax breakdown for clave "06" outgoing invoices
* ``_get_sii_invoice_dict_in()`` - Adds CuotaDeducible and BaseImponibleACoste to received invoices
* ``_get_sii_invoice_dict_out()`` - Adds BaseImponibleACoste to sent invoices
* ``_process_aeat_tax_base_info()`` / ``_process_aeat_tax_fee_info()`` - Track deductible amounts

