/**
 * Created by base on 30/8/17.
 */

var wxBox=$('.base-inlet-rate-wx');
var aliBox=$('.base-inlet-rate-alipay');
var jdBox=$('.base-inlet-rate-jdpay');

//费率是否存在
if(OPEN_D0 != 'True'){
    $('.base-inlet-d0').remove();
}
if(OPEN_DINE != 'True'){
    $('[pay-scene="scene-dine"]').parent().remove();
    $('[pay-type="type-dine"]').remove();
}
if(WX_0_RATE!='True'){
    wxBox.find('.base-type-choose').eq(1).parent().remove();
    wxBox.find('.base-rate-zero').remove();
}
if(ALI_0_RATE!='True'){
    aliBox.find('.base-type-choose').eq(1).parent().remove();
    aliBox.find('.base-rate-zero').remove();
}

//费率选择变量
if(WX=='True'){
    $('[value="wx"]').click();
    wxBox.show();
}
if(WX_OFFLINE=='True'){
    wxBox.find('input[pay-scene="scene-offline"]').click();
}
if(WX_ONLINE=='True'){
    wxBox.find('input[pay-scene="scene-online"]').click();
}
if(WX_DINE=='True'){
    wxBox.find('input[pay-scene="scene-dine"]').click();
}

if(WX_D0=='True'){
    wxBox.find('.base-inlet-d0').find('input[type="checkbox"]').click();
    wxBox.find('.base-inlet-d0').find('.base-hide').show();
}
if(ALI=='True'){
    $('[value="alipay"]').click();
    aliBox.show();
}
if(ALI_D0=='True'){
    aliBox.find('.base-inlet-d0').find('input[type="checkbox"]').click();
    aliBox.find('.base-inlet-d0').find('.base-hide').show();
}


if(JD=='True'){
    $('[value="jdpay"]').click();
    jdBox.show();
}




$('.base-rate-common [type="text"]').each(function(){
    if($(this).val() != ''){
        $(this).removeAttr('disabled');
        $(this).parent().siblings().find('input').removeAttr('disabled').attr('placeholder','请输入费率');
        $(this).parent().siblings().find('i').addClass('checked');
    }
});
$('.base-rate-zero [type="text"]').each(function(){
    if($(this).attr('diff-val') != ''){
        $(this).removeAttr('disabled');
        $(this).parent().siblings().find('input').removeAttr('disabled').attr('placeholder','请输入费率');
        $(this).parent().siblings().find('i').addClass('checked');
    }
});



$('.base-type-choose').click(function(){
    var nextObj=$(this).parents('.base-inlet-form').next();
    var rateBox=$(this).parents('.base-inlet-form').siblings('.base-rate-choose');
    var dtId=$(this).parents('.base-inlet-form').siblings('.base-inlet-scene-input');
    var rateInputBox=$(this).parents('.base-inlet-form').siblings('.base-inlet-rate');
    var d0Box=$(this).parents('.base-inlet-form').siblings('.base-inlet-rate').find('.base-inlet-d0');

    if($(this).val()=='1'){
        nextObj.show();
        rateBox.show();
        d0Box.find('input').removeAttr('disabled');
        rateInputBox.find('.base-rate-zero').hide();
        rateInputBox.find('.base-rate-zero').find('i').removeClass('checked');
        rateInputBox.find('.base-rate-zero').find('input').attr('disabled','disabled');
        if(nextObj.find('input[pay-scene="scene-online"]').is(':checked') || nextObj.find('input[pay-scene="scene-offline"]').is(':checked')){
            d0Box.show();
            rateInputBox.show();
            rateInputBox.find('.base-rate-common').show();
            dtId.show();
        }
        if(nextObj.find('input[pay-scene="scene-dine"]').is(':checked')){
            rateInputBox.show();
            rateInputBox.find('.base-rate-common').show();
            $('tr[pay-type="type-dine"]').find('i').addClass('checked');
            $('tr[pay-type="type-dine"]').find('input').removeAttr('disabled');
        }
    }else{
        rateInputBox.show();
        nextObj.hide();
        rateBox.show();
        dtId.hide();
        d0Box.hide();
        d0Box.find('input').attr('disabled','disabled');
        rateInputBox.find('.base-rate-common').hide();
        rateInputBox.find('.base-rate-common').find('i').removeClass('checked');
        rateInputBox.find('.base-rate-common').find('input').attr('disabled','disabled');
        rateInputBox.find('.base-rate-zero').show();
    }
})//通道类型选择

$('.base-inlet-payment [type="checkbox"]').on('click',function(){
    var selfObj=$('.base-inlet-rate-'+$(this).val());
    if($(this).is(':checked')){
        selfObj.show();
        judgeScene();
    }else{
        selfObj.hide();
        selfObj.find('.base-icon-checkbox').removeClass('checked');
        selfObj.find('input[type="text"]').attr('disabled','disabled');
    }
})//支付方式选择

$('.base-inlet-scene [type="checkbox"]').on('change',function(){
    judgeScene();
})//交易场景选择

function judgeScene(){
    $('.base-inlet-scene input[type="checkbox"]').each(function(){
        var obj=$(this).parents('.base-inlet-scene').next();
        var rateBox=$(this).parents('.base-inlet-scene').siblings('.base-inlet-rate');
        var rateBoxCom=rateBox.find('.base-rate-common');
        var d0Box=$(this).parents('.base-inlet-scene').siblings('.base-inlet-rate').find('.base-inlet-d0');
        if($(this).is(':checked')){
            rateBox.show();
            rateBoxCom.show();
            if($(this).val()=='online' || $(this).val()=='offline'){
                d0Box.show();
                obj.show();
                if(d0Box.find('input[type="checkbox"]').is(':checked')){
                    d0Box.find('input[type="text"]').removeAttr('disabled');
                }
            }else if($(this).val()=='dine'){
                $(this).parents('.base-inlet-pay').find('[pay-type="type-'+$(this).val()+'"]').find('i').addClass('checked');
                $(this).parents('.base-inlet-pay').find('[pay-type="type-'+$(this).val()+'"]').find('input[type="text"]').removeAttr('disabled');
            }
            $(this).attr('checked','checked');
            $(this).parents('.base-inlet-pay').find('[pay-type="type-'+$(this).val()+'"]').show();
            $(this).parents('.base-inlet-scene').next().find('div[pay-scene="scene-'+$(this).val()+'"]').show();
            $(this).parents('.base-inlet-scene').next().find('div[pay-scene="scene-'+$(this).val()+'"]').find('input').removeAttr('disabled');
        }else{
            $(this).removeAttr('checked');
            $(this).parents('.base-inlet-pay').find('[pay-type="type-'+$(this).val()+'"]').find('i').removeClass('checked');
            $(this).parents('.base-inlet-pay').find('[pay-type="type-'+$(this).val()+'"]').find('input').attr('disabled','disabled');
            $(this).parents('.base-inlet-pay').find('[pay-type="type-'+$(this).val()+'"]').hide();
            $(this).parents('.base-inlet-scene').next().find('div[pay-scene="scene-'+$(this).val()+'"]').hide();
            $(this).parents('.base-inlet-scene').next().find('div[pay-scene="scene-'+$(this).val()+'"]').find('input').attr('disabled','disabled');

            if(!($(this).parent().siblings().find('input[pay-scene="scene-online"]').is(':checked')) && !($(this).parent().siblings().find('input[pay-scene="scene-offline"]').is(':checked'))){
                obj.hide();
                d0Box.hide();
                d0Box.find('input[type="text"]').attr('disabled','disabled');
            }
            if(!($(this).parent().siblings().find('input[pay-scene="scene-online"]').is(':checked')) && !($(this).parent().siblings().find('input[pay-scene="scene-offline"]').is(':checked')) && !($(this).parent().siblings().find('input[pay-scene="scene-dine"]').is(':checked'))){
                rateBoxCom.hide();
            }
        }
    });
}judgeScene();//交易场景选择


//d0业务
$('.base-rate-d0').click(function(){
    if($(this).is(':checked')){
        $(this).parent().next('.base-hide').show();
        $(this).parent().next('.base-hide').find('input').removeAttr('disabled');
    }else{
        $(this).parent().next('.base-hide').hide();
        $(this).parent().next('.base-hide').find('input').attr('disabled','disabled');
    }
});


$('.base-inlet-table i').on('click',function(){
    if($(this).hasClass('disabled')){
        return;
    }
    if($(this).hasClass('checked')){
        $(this).removeClass('checked');
        $(this).parent('td').siblings('td').find('input').attr('disabled','disabled');
        $(this).parent('td').siblings('td').find('input').removeAttr('placeholder');
    }else{
        $(this).addClass('checked');
        $(this).parent('td').siblings('td').find('input').removeAttr('disabled');
        $(this).parent('td').siblings('td').find('input').attr('placeholder','请输入费率');
    }
});//费率输入选择

//D0控制开关判断
if(OPEN_D0 != 'True'){
    $('.dt-dzero-show,.dt-dzero-choose').remove();
};


if(WX_ZERO=='True'){
    wxBox.find('.base-type-choose').eq(1).click();
    wxBox.find('.base-rate-common').hide();
    wxBox.find('.base-rate-choose').hide();
    wxBox.find('.base-inlet-scene').hide();
    wxBox.find('.base-inlet-scene-input').hide();
    wxBox.find('.base-rate-zero').show();
}
if(ALI_ZERO=='True'){
    aliBox.find('.base-type-choose').eq(1).click();
    aliBox.find('.base-rate-common').hide();
    aliBox.find('.base-rate-choose').hide();
    aliBox.find('.base-inlet-scene').hide();
    aliBox.find('.base-inlet-scene-input').hide();
    aliBox.find('.base-rate-zero').show();
}

//银联选择初始化
if( $('.base-inlet-rate-unionpay input').val() !== '' ){
    $('input[value="unionpay"]').click();
}