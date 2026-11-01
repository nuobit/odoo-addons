## Product images

The backend has two independent settings: **Template Main Image**
controls the template's image list; **Variant Main Image** controls each
variant's own list. Both settings offer the same choices:

- **Don't use main image**: export only the extra images.
- **Use main image as first image**: put the main image before the extra
  images.
- **Use main image as last image**: put the main image after the extra
  images.

Extra images retain their sequence order. Template and variant images
are not combined into a shared list.

For example, select **Don't use main image** for the template and **Use
main image as first image** for variants to retain the template's
extra-image gallery while showing each selected variant's main photo
first. When the main photo is the only image, both First and Last export
it.

When upgrading an existing backend, both settings retain the previous
shared choice. Newly created backends default to First for both
settings.

For each variant, the first selected image becomes its featured image
and the remaining images become its variation gallery. WooCommerce can
display that gallery when the shopper selects the variant. A variant
with no selected images has no own image or gallery and uses
WooCommerce's parent fallback.

Export the product again after changing its images or either setting.
The export also clears previous gallery assignments when there are no
remaining additional images.
