openerp.pos_discount_payment = function(instance){
    var module   = instance.point_of_sale;
    var QWeb = instance.web.qweb;
	_t = instance.web._t;
    var round_pr = instance.web.round_precision

    QWeb.add_template('/pos_discount_payment/static/src/xml/discount.xml');

    module.PosWidget.include({
        build_widgets: function(){
            var self = this;
            this._super();
       
            
            if(this.pos.config.iface_cashdrawer){
                return;
            }

            var discount = $(QWeb.render('discountButton'));

            discount.click(function(){
                try{
                    var model = new instance.web.Model("res.users"); 
                    
                    var currentOrder = self.pos.get('selectedOrder');
                    var discount_payment;
                    _.each(self.pos.cashregisters, function(cashregister) {
                        //console.log(cashregister.journal.discount);
                        if(cashregister.journal.discount) discount_payment = cashregister;
                    });
                    
                    var paymentLines = currentOrder.get('paymentLines');
                    
                    if (paymentLines.length) {
                    /* Delete existing discount line*/
                        _.each(paymentLines.models, function(paymentLine) {
                            if (paymentLine.cashregister.journal.name==discount_payment.journal.name){
                                paymentLine.destroy();
                            }
                        });
                    } 
                    self.pos.get('selectedOrder').addPaymentline(discount_payment);
                    self.pos_widget.screen_selector.set_current_screen('payment');
                }catch(err){
                    console.log(err);
                }
            });

            //discount.appendTo(this.$('.control-buttons'));
            //this.$('.control-buttons').removeClass('oe_hidden');
        },
    });
    module.Order = module.Order.extend({
        
       getDiscountTotal: function() {
            return round_pr((this.get('orderLines')).reduce((function(sum, orderLine) {
                return sum + ( (orderLine.get_discount()) * orderLine.get_quantity());
            }), 0), this.pos.currency.rounding);
        },
        
        
        
        
       
    });
    module.Orderline = module.Orderline.extend({
        get_base_price:    function(){
            var rounding = this.pos.currency.rounding;
            return round_pr((this.get_unit_price() - this.get_discount()) * this.get_quantity(), rounding);
        },
        set_discount: function(discount){
            var disc = Math.max(parseFloat(discount) || 0, 0);
            this.discount = disc;
            this.discountStr = '' + disc;
            this.trigger('change',this);
        },
        get_all_prices: function(){
            var base = round_pr(this.get_quantity() * (this.get_unit_price() - this.get_discount()), this.pos.currency.rounding);
            var totalTax = base;
            var totalNoTax = base;
            var taxtotal = 0;

            var product =  this.get_product();
            var taxes_ids = product.taxes_id;
            var taxes =  this.pos.taxes;
            var taxdetail = {};
            var product_taxes = [];

            _(taxes_ids).each(function(el){
                product_taxes.push(_.detect(taxes, function(t){
                    return t.id === el;
                }));
            });

            var all_taxes = _(this.compute_all(product_taxes, base)).flatten();

            _(all_taxes).each(function(tax) {
                if (tax.price_include) {
                    totalNoTax -= tax.amount;
                } else {
                    totalTax += tax.amount;
                }
                taxtotal += tax.amount;
                taxdetail[tax.id] = tax.amount;
            });

            return {
                "priceWithTax": totalTax,
                "priceWithoutTax": totalNoTax,
                "tax": taxtotal,
                "taxDetails": taxdetail,
            };
        },
        
    });
    /*module.PaypadWidget = module.PosBaseWidget.extend({
        
        
        template: 'PaypadWidget',
        renderElement: function() {
            var self = this;
            this._super();
            
            _.each(self.pos.cashregisters,function(cashregister) {
                
                if(!cashregister.journal.discount){
                    var button = new module.PaypadButtonWidget(self,{
                    pos: self.pos,
                    pos_widget : self.pos_widget,
                    cashregister: cashregister,
                });
                button.appendTo(self.$el);
                }    
                    
            });
        }
    });*/

};

