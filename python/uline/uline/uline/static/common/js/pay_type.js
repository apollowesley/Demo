/**
 * Created by apple on 18/4/17.
 */

//D0控制开关判断
if(OPEN_D0 != 'True'){
    $('.dt-dzero-show,.dt-dzero-choose').remove();
}


function payShow(_this,showbox){
    var showBox=$(showbox);
    if(_this.is(':checked')){
        showBox.show();
        showBox.find('input[type="text"]').removeAttr('disabled');
    }else{
        showBox.hide();
        showBox.find('input[type="text"]').attr('disabled',true);
    }
}

//围餐零费率
$('input[name="use_dine"]').click(function(){
    if($(this).is(':checked')){
        $('.table-dine').show();
        $(this).val('1');
    }else{
        $('.table-dine').hide();
        $(this).val('0');
    }
});
$(function(){
    if($('input[name="use_dine"]').val()==1){
        $('.table-dine').show();
        $('#payTypeWechat').attr('checked',true);
        $('.pay-wechat').show();
        $('input[name="use_dine"]').attr('checked',true);
    }else{
        $('.table-dine').hide();
        $('input[name="use_dine"]').removeAttr('checked');
    }
    $('.table-dine input[type="checkbox"]').attr('checked',true);
});




$('#payTypeWechat').click(function(){
    payShow($(this),'.pay-wechat');
});
$('#payTypeAlipay').click(function(){
    payShow($(this),'.pay-alipay');
});
$('#payTypeJdpay').click(function(){
    payShow($(this),'.pay-jdpay');
});
$('#payTypeUnionpay').click(function(){
    payShow($(this),'.pay-unionpay');
});
$('#bankRateWechat').click(function(){
    payShow($(this),'.pay-wechat .dt-dzero-show');
});
$('#bankRateAlipay').click(function(){
    payShow($(this),'.pay-alipay .dt-dzero-show');
});


var wxN=0;
$('.pay-wechat  .table-role').each(function(){
    if(($(this).children().eq(2).find('input').val() != undefined && $(this).children().eq(2).find('input').val() != '') || ($(this).children().eq(3).find('input').val() != undefined && $(this).children().eq(3).find('input').val() != '')){
        $(this).children().eq(0).find('input').attr('checked',true);
        $(this).find('input[type="text"]').removeAttr('readonly');
        $('#payTypeWechat').attr('checked',true);
        $('.pay-wechat').show();
    }
    if($(this).children().eq(3).find('input').val() != undefined && $(this).children().eq(3).find('input').val() != ''){
        wxN++
    }
    if(wxN>0){
        $('#bankRateWechat').attr('checked',true);
    }else{
        $('#bankRateWechat').removeAttr('checked');
    }
});

var aliN=0;
$('.pay-alipay tr').each(function(){
    if(($(this).children().eq(2).find('input').val() != undefined && $(this).children().eq(2).find('input').val() != '') || ($(this).children().eq(3).find('input').val() != undefined && $(this).children().eq(3).find('input').val() != '')){
        $(this).children().eq(0).find('input').attr('checked',true);
        $(this).find('input[type="text"]').removeAttr('readonly');
        $('#payTypeAlipay').attr('checked',true);
        $('.pay-alipay').show();
    }
    if($(this).children().eq(3).find('input').val() != undefined && $(this).children().eq(3).find('input').val() != ''){
        aliN++;
    }
    if(aliN>0){
        $('#bankRateAlipay').attr('checked',true);
    }else{
        $('#bankRateAlipay').removeAttr('checked');
    }
});

var jdN=0;
$('.pay-jdpay tr').each(function(){
    if($(this).children().eq(2).find('input').val() != undefined && $(this).children().eq(2).find('input').val() != ''){
        $(this).children().eq(0).find('input').attr('checked',true);
        $(this).find('input[type="text"]').removeAttr('readonly');
        $('#payTypeJdpay').attr('checked',true);
        $('.pay-jdpay').show();
    }
});

if($('.pay-unionpay input').eq(0).val()!=''){
    $('#payTypeUnionpay').click();
    $('.pay-unionpay').show();
}

if($('#bankRateWechat').is(':checked')){
    $('.pay-wechat .dt-dzero-show').show()
}
if($('#bankRateAlipay').is(':checked')){
    $('.pay-alipay .dt-dzero-show').show()
}

$('button[type="submit"]').click(function(){
    if( !$('#payTypeWechat').is(':checked') && !$('#payTypeAlipay').is(':checked') && !$('#payTypeJdpay').is(':checked') ){
        $('.time-error').html('<p style="color:darkred;font-size:16px;">支付信息不能为空</p>');
        return false;
    }else{
        $('.time-error').html('');
    }
    if($('#bankRateWechat').is(':checked')){
        if($('#bankRatePayWechat').val()==''){
            $(this).siblings('.time-error').html('<p class="wx-tip" style="color:darkred;font-size:16px;">D0微信提现手续费不能为空</p>');
            return false;
        }
    }else{
        $('#bankRatePayWechat').val('');
        $(this).siblings('.time-error').find('.ali-tip').remove();
    }
    if($('#bankRateAlipay').is(':checked')){
        if($('#bankRatePayAlipay').val()==''){
            $(this).siblings('.time-error').html('<p class="ali-tip" style="color:darkred;font-size:16px;">D0支付宝提现手续费不能为空</p>');
            return false;
        }
    }else{
        $('#bankRatePayAlipay').val('');
        $(this).siblings('.time-error').find('.ali-tip').remove();
    }
});









