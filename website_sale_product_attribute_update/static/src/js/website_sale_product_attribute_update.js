$(document).ready(function () {

    function update_product_attributes(event_source) {
        var attribs_str = $(event_source).data('attribs');
        if (attribs_str != undefined) {
            var attribs_l = attribs_str.split(',');
            var $attrib = $('#attributes');
            $attrib.empty();
            $.each(attribs_l, function (index, value) {
                var attrib_t = value.split('-');
                $attrib.append($("<strong>").text(attrib_t[0]));
                $attrib.append(": ");
                $attrib.append($("<span>").text(attrib_t[1]));
                $attrib.append($("<br>"));
            });
        }
    }

    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;

        $(oe_website_sale).on('change', 'input.js_product_change', function (ev) {
            update_product_attributes(this)
        });

        $('div.js_product', oe_website_sale).each(function () {
            $('input.js_product_change', this).first().trigger('change');
        });
    });
});
