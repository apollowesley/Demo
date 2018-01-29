/**
 * Created by base on 30/8/17.
 */
var wxBox=$('.base-inlet-pay').eq(0);
var aliBox=$('.base-inlet-pay').eq(1);
var jdBox=$('.base-inlet-pay').eq(2);
 //是否存在费率判断
if(HAS_WX_ZERO=='True'){
    wxBox.find('.base-rate-common-box').remove();
}else{
    wxBox.find('.base-rate-zero-box').remove();
}
if(HAS_ALI_ZERO=='True'){
    aliBox.find('.base-rate-common-box').remove();
}else{
    aliBox.find('.base-rate-zero-box').remove();
}
if(HAS_WX_OFFLINE!='True'){
    wxBox.find('[pay-scene="scene-offline"]').parent().remove();
    wxBox.find('[pay-type="type-offline"]').remove();
}
if(HAS_WX_ONLINE!='True'){
    wxBox.find('[pay-scene="scene-online"]').parent().remove();
    wxBox.find('[pay-type="type-online"]').remove();
}
if(HAS_WX_DINE!='True'){
    wxBox.find('[pay-scene="scene-dine"]').parent().remove();
    wxBox.find('[pay-type="type-dine"]').remove();
}
if(HAS_WX_D1!='True'){
    wxBox.find('.base-rate-choose').find('.base-inlet-checkbox').eq(0).remove();
    wxBox.find('[pay-rate="rate-d0"]').remove();
}
if(HAS_WX_D0!='True'){
    wxBox.find('.base-inlet-d0').remove();
}
if(HAS_ALI_D1!='True'){
    aliBox.find('.base-rate-choose').find('.base-inlet-checkbox').eq(0).remove();
    aliBox.find('[pay-rate="rate-d1"]').remove();
}
if(HAS_ALI_D0!='True'){
    aliBox.find('.base-inlet-d0').remove();
}
if(HAS_ALI_OFFLINE!='True'){
    aliBox.find('[pay-scene="scene-offline"]').parent().remove();
    aliBox.find('[pay-type="type-offline"]').remove();
}

//是否选择费率判断
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
if(WX_ZERO=='True'){
    wxBox.find('.base-rate-zero-box').children('div').show();
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
if(ALI_ZERO=='True'){
    wxBox.find('.base-rate-zero-box').children('div').show();
}
if(ALI_OFFLINE=='True'){

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
    if($(this).val()=='1'){
        nextObj.show();
        rateBox.show();
        dtId.show();
        rateInputBox.find('.base-rate-zero').hide();
        rateInputBox.find('.base-rate-zero').find('i').removeClass('checked');
        rateInputBox.find('.base-rate-zero').find('input').attr('disabled','disabled');
        rateInputBox.find('.base-rate-common').show();
    }else{
        nextObj.hide();
        rateBox.hide();
        dtId.hide();
        rateInputBox.find('.base-rate-common').hide();
        rateInputBox.find('.base-rate-common').find('i').removeClass('checked');
        rateInputBox.find('.base-rate-common').find('input').attr('disabled','disabled');
        rateInputBox.find('.base-rate-zero').show();
    }
})//通道类型选择

$('.base-inlet-payment [type="checkbox"]').on('click',function(){
    var selfObj=$('.base-inlet-rate-'+$(this).val());
    if($(this).is(':checked')){
        if($(this).val()=='unionpay'){
            selfObj.find('input[type="text"]').removeAttr('disabled');
        }
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

$('.base-inlet-scene [type="checkbox"]').on('change',function(){
    judgeRate();
})//结算周期选择


function judgeRate(){
    if($('.base-rate-choose input[type="radio"]:checked').val()=='d1'){
        $('[pay-rate="rate-d1"]').show();
    }else if($('.base-rate-choose input[type="radio"]:checked').val()=='d0'){
        $('[pay-rate="rate-d0"]').show();
    }//费率
}
judgeRate();

function judgeScene(){
    $('.base-inlet-scene input[type="checkbox"]').each(function(){
        var obj=$(this).parents('.base-inlet-scene').next();
        var d0Box=$(this).parents('.base-inlet-scene').next().find('.base-inlet-d0');
        if($(this).is(':checked')){
            obj.show();
            if($(this).val()=='online' || $(this).val()=='offline'){
                d0Box.show();
                if(d0Box.find('input[type="checkbox"]').is(':checked')){
                    d0Box.find('input[type="text"]').removeAttr('disabled');
                }
                $(this).parent().siblings('div').children('[value="dine"]').attr('disabled','disabled');
            }else if($(this).val()=='dine'){
                $(this).parents('.base-inlet-pay').find('[pay-type="type-'+$(this).val()+'"]').find('i').addClass('checked');
                $(this).parents('.base-inlet-pay').find('[pay-type="type-'+$(this).val()+'"]').find('input[type="text"]').removeAttr('disabled');
                $('.base-inlet-dine-box').show();
                $(this).parent().siblings('div').children('input').attr('disabled','disabled');
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
                d0Box.hide();
                d0Box.find('input[type="text"]').attr('disabled','disabled');
                $(this).parent().siblings('div').children('[value="dine"]').removeAttr('disabled');
            }
            if(!($(this).parent().siblings().find('input[pay-scene="scene-online"]').is(':checked')) && !($(this).parent().siblings().find('input[pay-scene="scene-offline"]').is(':checked')) && !($(this).parent().siblings().find('input[pay-scene="scene-dine"]').is(':checked'))){
                obj.hide();
            }
            if($(this).val()=='dine'){
                $('.base-inlet-dine-box').hide();
                $(this).parent().siblings('div').children('input').removeAttr('disabled');
            }
        }
    });
}//交易场景选择
judgeScene();


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


//d0业务
$('.base-rate-d0').on('click',function(){
    if($(this).is(':checked')){
        $(this).parent().next('.base-hide').show();
        $(this).parent().next('.base-hide').find('input').removeAttr('disabled');
    }else{
        $(this).parent().next('.base-hide').hide();
        $(this).parent().next('.base-hide').find('input').attr('disabled','disabled');
    }
});


//D0控制开关判断
if(OPEN_D0 != 'True'){
    $('.dt-dzero-show,.dt-dzero-choose').remove();
}

$('button[type="submit"]').click(function(){

});

//银联选择初始化
if( $('.base-inlet-rate-unionpay input').val() !== '' ){
    $('input[value="unionpay"]').click();
}

