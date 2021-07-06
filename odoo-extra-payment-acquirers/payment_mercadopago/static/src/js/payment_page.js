odoo.define('payment_mercadopago.mercadopago_payment',function(require){
    "use_strict";

    var core = require('web.core');
	var ajax = require('web.ajax');
	var QWeb = core.qweb;

    $(document).ready(function (){

        if ($('.installments_value1') != null){ $(document).on('change',
                    '.installments_value1', function (event) { event.preventDefault();
                    $(this).parent().find('.installments1').val($(this).val()); $('#installments').val($(this).val());
                    }); }; $(document).on('change', '.cccc', function (event) { $('#cc_cvc').val($(this).val()); });
                    $(document).on('click', '[name="pm_id"]', function () {
                    $(document).find('div.panel-body').each(function() { $(this).removeClass('active');
                    $(this).find('.cc_cvc').val(''); }); $(this).parent().parent().addClass('active'); });
        $('#docType').val("DNI");
                    $('#installments').val("1");
                    console.log('$("#docTypeValue") >>>>>>>>>>>>>', $("#docTypeValue"))
                    console.log('$("#docTypeValue") >>>>>>>>>>>>>', document.getElementById("docTypeValue"))
                    if (document.getElementById("docTypeValue")){
                        console.log('in ifffffffffffff')
                        document.getElementById("docTypeValue").onchange = function(event) {
                                            console.log('asasasas >>>>>>>>>>>>>>>>>')
                                            event.preventDefault();
                                            var doctype = $("#docTypeValue").val();
                                            $('#docType').val(doctype);
                                        };
                                        if (document.getElementById("installments_value") != null){
                                        document.getElementById("installments_value").onchange = function(event) {
                                            event.preventDefault();
                                            var installments = $("#installments_value").val();
                                            $('#installments').val(installments);
                                        };};
                };

        $( ".mercadopago_installments" ).change(function(event) {
            var cur_i = this.options[this.selectedIndex].getAttribute('data-tax');
            console.log("cur_i : ",cur_i);
            if(cur_i != null){
                document.getElementById('total-financed').innerHTML = this.options[this.selectedIndex].text;
                showTaxes(cur_i);
            }
            }
            );
        function showTaxes(tax){
           var tax_split = tax.split('|');
           var CFT = tax_split[0].replace('CFT_', ''),
           TEA = tax_split[1].replace('TEA_', '');
           document.getElementById('cft').innerHTML = CFT;
           document.getElementById('tea').innerHTML = TEA;
       }
        console.log("Ready on load");
        var mpForm = $('#mp_form').html();
        var conceptName = ""

        $('select[name=payment_method]').on('change',function(e) {
            e.preventDefault();

            var checked_radio = $('input[type="radio"]:checked');
            var partner_id = $('.o_payment_form').data('partner-id')
            var csrf_token = $("input[name=csrf_token]").val()
            if (checked_radio.data('acquirer-id')){
                var acquirer_id = checked_radio.data('acquirer-id');
            }
            if (this.value == 'credit_debit') {
                $('#mp_form').html(mpForm);
                $('#payment_type_bank').addClass('hidden');
            }
            else if (this.value == 'cash') {
                $('#payment_type_bank').addClass('hidden');
                $('#mp_form').html('<input type="hidden" name="data_set" data-create-route="/payment/mercadopago/deposit"/>'+
                '<input type="hidden" name="partner_id" value='+partner_id+'></input>'+
                '<input type="hidden" name="acquirer_id" value='+acquirer_id+'></input>'+
                '<input type="hidden" name="payment_method" value='+this.value+'></input>'+
                '<input type="hidden" name="csrf_token" value='+csrf_token+'></input>');
            }
            else if (this.value == 'bank_transfer') {
                $('#payment_type_bank').removeClass('hidden');
                console.log(conceptName);
               $('#mp_form').html('<input type="hidden" name="data_set" data-create-route="/payment/mercadopago/deposit"/>'+
                '<input type="hidden" name="partner_id" value='+partner_id+'></input>'+
                '<input type="hidden" name="acquirer_id" value='+acquirer_id+'></input>'+
                '<input type="hidden" name="payment_method" value='+this.value+'></input>'+
                '<input type="hidden" name="payment_type_bank" value='+conceptName+'></input>'+
                '<input type="hidden" name="csrf_token" value='+csrf_token+'></input>');
//                 alert("Transfer Thai Gayo");
            }
        });

        $('select[name=payment_type_bank]').on('click', function(e) {
            e.preventDefault();
            console.log('>>>>>>',this.value);
            console.log('>>>>>>',$('select[name=payment_method]').val());
            conceptName = this.value;
            var checked_radio = $('input[type="radio"]:checked');
            var partner_id = $('.o_payment_form').data('partner-id');
            var csrf_token = $("input[name=csrf_token]").val();
            if (checked_radio.data('acquirer-id')){
                var acquirer_id = checked_radio.data('acquirer-id');
            }

            var mpForm = $('#mp_form').html();

            $('#mp_form').html('<input type="hidden" name="data_set" data-create-route="/payment/mercadopago/deposit"/>'+
            '<input type="hidden" name="partner_id" value='+partner_id+'></input>'+
            '<input type="hidden" name="acquirer_id" value='+acquirer_id+'></input>'+
            '<input type="hidden" name="payment_method" value='+$('select[name=payment_method]').val()+'></input>'+
            '<input type="hidden" name="payment_type_bank" value='+conceptName+'></input>'+
            '<input type="hidden" name="csrf_token" value='+csrf_token+'></input>');

        });

    });
})