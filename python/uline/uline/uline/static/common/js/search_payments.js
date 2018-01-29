/**
 * Created by apple on 26/5/17.
 */
var search_payment=$('select[name="channel"]');

$('select[name="trade_type"] option').hide();
$('select[name="trade_type"] option').eq(0).show();
if(search_payment.val()=='weixin'){
    $('select[name="trade_type"] option').show();
    $('option[value*="ALIPAY"]').hide();
    $('option[value*="JDPAY"]').hide();
}else if(search_payment.val()=='alipay'){
    $('option[value*="ALIPAY"]').show();
}else if(search_payment.val()=='jdpay'){
    $('option[value*="JDPAY"]').show();
}else if(search_payment.val()==''){
    $('select[name="trade_type"] option').show();
}
function paymentStatus(){
    $('select[name="trade_type"] option').hide();
    $('select[name="trade_type"] option').eq(0).show();
    $('select[name="trade_type"]').val('');
    if(search_payment.val()=='weixin'){
        $('select[name="trade_type"] option').show();
        $('option[value*="ALIPAY"]').hide();
        $('option[value*="JDPAY"]').hide();
    }else if(search_payment.val()=='alipay'){
        $('option[value*="ALIPAY"]').show();
    }else if(search_payment.val()=='jdpay'){
        $('option[value*="JDPAY"]').show();
    }else if(search_payment.val()==''){
        $('select[name="trade_type"] option').show();
    }
}
search_payment.on('change',function(){
    paymentStatus();
});













