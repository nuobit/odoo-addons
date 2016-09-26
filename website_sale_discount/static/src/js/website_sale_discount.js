$(document).ready(function () {
    $('.oe_website_sale').find(".oe_cart input.js_quantity").off('change');

    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;

        $(oe_website_sale).find(".oe_cart input.js_quantity").on("change", function () {
            var $input = $(this);
            if ($input.data('update_change')) {
                return;
            }
            var value = parseInt($input.val(), 10);
            var $dom = $(this).closest('tr');
            //var default_price = parseFloat($dom.find('.text-danger > span.oe_currency_value').text());
            var $dom_optional = $dom.nextUntil(':not(.optional_product.info)');
            var line_id = parseInt($input.data('line-id'),10);
            var product_id = parseInt($input.data('product-id'),10);
            var product_ids = [product_id];
            $dom_optional.each(function(){
                product_ids.push($(this).find('span[data-product-id]').data('product-id'));
            });
            if (isNaN(value)) value = 0;
            $input.data('update_change', true);
            openerp.jsonRpc("/shop/cart/update_json", 'call', {
                'line_id': line_id,
                'product_id': parseInt($input.data('product-id'),10),
                'set_qty': value})
            .then(function (data) {
                $input.data('update_change', false);
                if (value !== parseInt($input.val(), 10)) {
                    $input.trigger('change');
                    return;
                }
                if (!data.quantity) {
                    location.reload(true);
                    return;
                }
                var $q = $(".my_cart_quantity");
                $q.parent().parent().removeClass("hidden", !data.quantity);
                $q.html(data.cart_quantity).hide().fadeIn(600);

                $input.val(data.quantity);
                $("td[name='price'] > span[data-oe-id="+line_id+"] > span.oe_currency_value").text(data['price_unit']);
                $("td[name='discount'] > span[data-oe-id="+line_id+"]").text(data['discount']);
                $("td[name='subtotal'] > span[data-oe-id="+line_id+"] > span.oe_currency_value").text(data['price_subtotal']);
                $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);
                $("#cart_total").replaceWith(data['website_sale.total']);
            });
        });
    });
});
