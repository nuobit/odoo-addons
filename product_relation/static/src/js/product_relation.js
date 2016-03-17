openerp.product_relation = function(instance, local) {
    var QWeb = openerp.web.qweb;
        _t = instance.web._t;

    /*
    instance.web.form.FieldSelection.include({
        init: function (field_manager, node) {
            //alert('kk');

            //var y = $("[data-field='product_id']");
            //alert('y');
            this._super(field_manager, node);
        }
    });
    */


    local.Mywidget = instance.web.form.FieldChar.extend({
        template : "test",
        init: function (view, code) {
            this._super(view, code);
            console.log('loading...');
        }
    });

    instance.web.form.widgets.add('test', 'openerp.product_relation.Mywidget');

    local.Mywidget2 = instance.web.form.FieldSelection.extend({
        //template : "test",
        init: function (view, code) {
            this._super(view, code);
            console.log('pepe...');
        },
        events: {
            "change select": "select_onchange",
        },
        select_onchange: function(event) {
            var product_id = parseInt(this.$('select').val(), 10);
            var model = new instance.web.Model("pr.wizard");
            var wizard_id;
            //modelt('name', 'kkk dsds');
            model.call("my_method", {context: new instance.web.CompoundContext(), product_id: product_id}).then(function(result) {
                console.log(result['hello']);
                wizard_id = result['id'];
                //alert(result['product_id']);
                //this.$el.append("<div>Hello " + result["hello"] + "</div>");
                // will show "Hello world" to the user
            });

            console.log('clocked...');
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'pr.wizard',
                view_type: 'form',
                view_mode: 'form',
                res_id: wizard_id, //$(event.currentTarget).data('id'),
                views: [[false, 'form']],
                target: 'new',
                /*
                flags: {
                        search_view: true,
                        display_title: true,
                        pager: true,
                        list: {selectable: false}
                    }*/
            });
        },
    });

    instance.web.form.widgets.add('test2', 'openerp.product_relation.Mywidget2');


    /*
    instance.web.View.include({
        load_view: function(context) {
            var self = this;
            var view_loaded_def;
            $('#oe_linking_e').click(this.on_preview_view_button);

            //this is button class which call method for open your form.

            return self._super(context);
        },

        //method which open form
        on_preview_view_button: function(e){
            e.preventDefault();
                this.do_action({
                    name: _t("View name"),
                    type: "ir.actions.act_window",
                    res_model: "pr.wizard",
                    domain : [],
                    views: [[false, "form"],[false, "tree"]],
                    target: 'new',
                    context: {},
                    view_type : 'list',
                    view_mode : 'list'
                });
        }
    });
    */
};