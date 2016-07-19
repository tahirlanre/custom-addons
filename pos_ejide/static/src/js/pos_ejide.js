//To Do
//Disallow sales when no available quantity  DONE

openerp.pos_ejide = function(instance){
    var module = instance.point_of_sale;
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var PosModelSuper = module.PosModel;
    var round_di = instance.web.round_decimals;
	
    module.PosModel = module.PosModel.extend({
        load_server_data: function(){
            var self = this;
            var loaded = PosModelSuper.prototype.load_server_data.call(this);

            loaded = loaded.then(function(){
                return self.fetch(
                    'product.product',
                    ['qty_available'],
                    [['sale_ok','=',true],['available_in_pos','=',true]],
                    {'location': self.config.stock_location_id[0]}
                );

            }).then(function(products){
                $.each(products, function(){
                    $.extend(self.db.get_product_by_id(this.id) || {}, this)
                });
                return $.when()
            })
            return loaded;
        },
	});
    module.Order = module.Order.extend({
        
       initialize: function(attributes){
           Backbone.Model.prototype.initialize.apply(this, arguments);
            this.pos = attributes.pos;
            this.sequence_number = this.pos.pos_session.sequence_number++;
            this.uid =     this.generateUniqueId();
            this.invoice_no = undefined;
            this.payment_no = undefined;
            this.payment_detail = undefined;
            this.set({
                creationDate:   new Date(),
                orderLines:     new module.OrderlineCollection(),
                paymentLines:   new module.PaymentlineCollection(),
                name:           _t("Order ") + this.uid,
                client:         null,
            });
            this.payment_amount = 0;
            this.selected_orderline   = undefined;
            this.selected_paymentline = undefined;
            this.screen_data = {};  // see ScreenSelector
            this.receipt_type = 'receipt';  // 'receipt' || 'invoice'
            this.temporary = attributes.temporary || false;
            return this;
        },
      
        addProduct: function(product, options){
            
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new instance.point_of_sale.Orderline({}, {pos: this.pos, order: this, product: product});
            var currentOrderLines = this.pos.get('selectedOrder').get('orderLines');
            var prod_qty = attr.qty_available;
            
      
            if (prod_qty <= 0 && attr.type != 'service') {
                
                alert ('Not enough stock !');
                return;
            }
            
            if (attr.type == 'service') {
                console.log('service');
                if(options.quantity !== undefined){
                    line.set_quantity(options.quantity);
                }
                if(options.price !== undefined){
                    line.set_unit_price(options.price);
                }
                if(options.discount !== undefined){
                    line.set_discount(options.discount);
                }
    
                var last_orderline = this.getLastOrderline();
                if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
                    last_orderline.merge(line);
                }else{
                    this.get('orderLines').add(line);
                }
                this.selectLine(this.getLastOrderline());
            }
            
            if (prod_qty > 0 && attr.type != 'service') {
                //console.log('Product');
                add_prod = true
                if (currentOrderLines.length > 0) {
                    (currentOrderLines).each(_.bind( function(item) {
                        if (attr.id == item.get_product().id && prod_qty < item.get_quantity()+1) {
                            add_prod = false;
                            alert ('Not enough stock !');
                        }
                    }, this));
                } 
                if (add_prod) {
                    if(options.quantity !== undefined){
                        line.set_quantity(options.quantity);
                    }
                    if(options.price !== undefined){
                        line.set_unit_price(options.price);
                    }
                    if(options.discount !== undefined){
                        line.set_discount(options.discount);
                    }
        
                    var last_orderline = this.getLastOrderline();
                    if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
                        last_orderline.merge(line);
                    }else{
                        this.get('orderLines').add(line);
                    }
                    this.selectLine(this.getLastOrderline());
                }
            }
        },
        
        
    });
	
    module.PaymentScreenWidget.include({
        
        show: function(){
            this._super();
            var self = this;

        },
     	
        validate_order: function(options) {
            var self = this;
            options = options || {};

            var currentOrder = this.pos.get('selectedOrder');

            if(currentOrder.get('orderLines').models.length === 0){
                this.pos_widget.screen_selector.show_popup('error',{
                    'message': _t('Empty Order'),
                    'comment': _t('There must be at least one product in your order before it can be validated'),
                });
                return;
            }

            var plines = currentOrder.get('paymentLines').models;
            for (var i = 0; i < plines.length; i++) {
                if (plines[i].get_type() === 'bank' && plines[i].get_amount() < 0) {
                    this.pos_widget.screen_selector.show_popup('error',{
                        'message': _t('Negative Bank Payment'),
                        'comment': _t('You cannot have a negative amount in a Bank payment. Use a cash payment method to return money to the customer.'),
                    });
                    return;
                }
            }
			
            var olines = currentOrder.get('orderLines').models;
            for (var i = 0; i < olines.length; i++) {
                console.log(olines[i]);
                if(olines[i].product.qty_available < olines[i].quantity && olines[i].get_product().type != 'service'){
                    this.pos_widget.screen_selector.show_popup('error',{
                        message: _t('Out of Stock'),
                        comment: _t('Not enough stock for product "' + olines[i].product.display_name + '"'),
                    });
					return;
                }
            }

            if(!this.is_paid()){
                return;
            }

            // The exact amount must be paid if there is no cash payment method defined.
            if (Math.abs(currentOrder.getTotalTaxIncluded() - currentOrder.getPaidTotal()) > 0.00001) {
                var cash = false;
                for (var i = 0; i < this.pos.cashregisters.length; i++) {
                    cash = cash || (this.pos.cashregisters[i].journal.type === 'cash');
                }
                if (!cash) {
                    this.pos_widget.screen_selector.show_popup('error',{
                        message: _t('Cannot return change without a cash payment method'),
                        comment: _t('There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'),
                    });
                    return;
                }
            }

            if (this.pos.config.iface_cashdrawer) {
                    this.pos.proxy.open_cashbox();
            }

            if(options.invoice){
                // deactivate the validation button while we try to send the order
                this.pos_widget.action_bar.set_button_disabled('validation',true);
                this.pos_widget.action_bar.set_button_disabled('invoice',true);

                var invoiced = this.pos.push_and_invoice_order(currentOrder);

                invoiced.fail(function(error){
                    if(error === 'error-no-client'){
                        self.pos_widget.screen_selector.show_popup('error',{
                            message: _t('An anonymous order cannot be invoiced'),
                            comment: _t('Please select a client for this order. This can be done by clicking the order tab'),
                        });
                    }else{
                        self.pos_widget.screen_selector.show_popup('error',{
                            message: _t('The order could not be sent'),
                            comment: _t('Check your internet connection and try again.'),
                        });
                    }
                    self.pos_widget.action_bar.set_button_disabled('validation',false);
                    self.pos_widget.action_bar.set_button_disabled('invoice',false);
                });

                invoiced.done(function(){
                    self.pos_widget.action_bar.set_button_disabled('validation',false);
                    self.pos_widget.action_bar.set_button_disabled('invoice',false);
                    self.pos.get('selectedOrder').destroy();
                });

            }else{
                this.pos.push_order(currentOrder) 
                if(this.pos.config.iface_print_via_proxy){
                    var receipt = currentOrder.export_for_printing();
                    this.pos.proxy.print_receipt(QWeb.render('XmlReceipt',{
                        receipt: receipt, widget: self,
                    }));
                    this.pos.get('selectedOrder').destroy();    //finish order and go back to scan screen
                }else{
                    this.pos_widget.screen_selector.set_current_screen(this.next_screen);
                }
            }

            // hide onscreen (iOS) keyboard 
            setTimeout(function(){
                document.activeElement.blur();
                $("input").blur();
            },250);
        },
		
    });
	
    module.ReceiptScreenWidget.include({
        
        refresh: function() {
            var order = this.pos.get('selectedOrder');
			var customer = order.get_client();
			var partner = '';
			if(customer){
				partner = customer;
			}
            $('.pos-receipt-container', this.$el).html(QWeb.render('PosTicket',{
                    widget:this,
                    order: order,
					partner : partner,
                    orderlines: order.get('orderLines').models,
                    paymentlines: order.get('paymentLines').models,
                }));
        },
    });
    

	
}