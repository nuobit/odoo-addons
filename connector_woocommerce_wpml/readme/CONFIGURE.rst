Required WooCommerce Plugin
===========================

This module requires the **WooCommerce WPML API REST Extension** plugin to function properly.

Plugin URL: https://github.com/nuobit/woocommerce-wpml-api-rest-extension

This plugin is necessary to work around several bugs in the WPML REST API related to:

* Language parameter handling
* Retrieving language-specific product data
* Setting and updating content per language

Without this extension, the connector will not be able to properly synchronize multilingual content between Odoo and WooCommerce.
