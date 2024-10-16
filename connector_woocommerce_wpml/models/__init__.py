from . import backend
from . import binding
from . import product_public_category
from . import product_attribute
from . import product_attribute_value
from . import product
from . import product_template
from . import product_product
from . import res_lang


# TODO: ir_checksum needs to be adapted to wpml.
# from . import ir_checksum

# TODO: Res_partner, sale_order, sale_order_line and stock_picking are not
#  modified with wpml, but probably we need copy in this module to include
#  buttons and probably adapt some code ( in the other module we have language_id on backend)

from . import res_partner
from . import sale_order_line
from . import sale_order
from . import stock_picking
