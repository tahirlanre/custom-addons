openerp.pos_sambo = function(instance){
    var module   = instance.point_of_sale;
    var QWeb = instance.web.qweb;
	_t = instance.web._t;

    QWeb.add_template('/pos_sambo/static/src/xml/pos_sambo.xml');

    module.PosWidget.include({
        build_widgets: function(){
            var self = this;
            this._super();
            
            if(this.pos.config.iface_cashdrawer){
                return;
            }

            var debt = $(QWeb.render('debtButton'));

            debt.click(function(){
                self.pos_widget.screen_selector.set_current_screen('payment');

            });

            debt.appendTo(this.$('.control-buttons'));
            this.$('.control-buttons').removeClass('oe_hidden');
        },
    });

};

