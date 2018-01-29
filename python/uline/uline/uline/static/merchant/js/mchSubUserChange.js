/**
 * Created by apple on 12/4/17.
 */

var sub_user_host=window.location.protocol + '//' + window.location.host;
function checkSubUser(mch_sub_id,_xsrf,_status){
    $.ajax({
        type : "get",  //提交方式
        url : sub_user_host+"/merchant/settings/sub_user/info",//路径
        data : {
            "mch_sub_id" : mch_sub_id,
        },//数据，这里使用的是Json格式进行传输
        success : function(result) {//返回数据根据结果进行相应的处理
            if ( result.code ==200 ) {
                $('.glyphicon-ok').hide();
                $('.form-group').removeClass('has-success');
                if(_status==1){
                    $('#form-base input').attr('readonly',true);
                    $('#form-base select').attr('disabled',true);
                    $('#form-base').addClass('noborder');
                    $('#send_sub_user').hide();
                }else{
                    $('#form-base input').attr('readonly',false);
                    $('#form-base select').attr('disabled',false);
                    $('#check_login').attr('readonly',true);
                    $('#form-base').removeClass('noborder');
                    $('#send_sub_user').show();
                }
                $('#check_login').val(result.data.login_name);
                $('#check_name').val(result.data.mch_sub_name);
                $('#check_phone').val(result.data.phone);
                $('#check_email').val(result.data.email);
                if(result.data.status==1){
                    $('#subUserSelect').val('1')
                }else{
                    $('#subUserSelect').val('2')
                }
            } else {

            }
        }
    });
}

$('.bind_wx_code').on('click',function() {
    //绑定微信弹出微信二维码窗口
    var mch_sub_id = $(this).attr('bindvalue');
    var _this=$(this);
    $.ajax({
        type: "get",  //提交方式
        url: sub_user_host + "/merchant/settings/sub_user/getqrcode",//路径
        data: {
            "mch_sub_id": mch_sub_id
        },//数据，这里使用的是Json格式进行传输
        success: function (result) {//返回数据根据结果进行相应的处理
            if (result.code == 200) {
                $('#bindingwx').modal('show');
                $('#qrimg').attr('src', result.scan_url);

            } else {
                clearInterval(timer);
                errorTipBtn(result.msg)

            }
        }
    });
    var timer=setInterval(function(){
        $.ajax({
            type: "get",  //提交方式
            url: sub_user_host + "/merchant/settings/sub_user/bindingstatus",//路径
            data: {
                "mch_sub_id": mch_sub_id,
                "binding": 1
            },//数据，这里使用的是Json格式进行传输
            success: function (result) {//返回数据根据结果进行相应的处理
                if (result.code == 200 && result.msg == 1 ) {
                    clearInterval(timer);
                    $('#bindingwx').hide();
                     window.location.reload();
                }

            }
        });
    },2000);
    $('#bindingwx').on('hidden.bs.modal', function (e) {
        clearInterval(timer);
    })
});

$('.unbind_wx_code').on('click',function(){
     var mch_sub_id = $(this).attr('bindvalue');
    //var _this=$(this);
    $('body').ulaiberLoading({loadingText:'确定要解绑吗',loadingType:'comfirm',sureFunction:function(){

        $.ajax(
        {
            type: "get",  //提交方式
            url: sub_user_host + "/merchant/settings/sub_user/bindingstatus",//路径
            data: {
                "mch_sub_id": mch_sub_id,
                "binding": 2
            },//数据，这里使用的是Json格式进行传输
            success: function (result) {
                  if (result.code == 200 && result.msg == 2) {
                      window.location.reload();

            } else {
                      errorTipBtn(result.msg)

            }
            }//返回数据根据结果进行相应的处理
        }
    )
    }});


})






//查看员工账号
$('.check_btn').on('click',function(){
    var mch_sub_id=$(this).parent().siblings('.mch_sub_id').text(),
        _xsrf=$('input[name="_xsrf"]').val();
    $('.change-error').html('');
    checkSubUser(mch_sub_id,_xsrf,1);
})







//编辑员工账号
$('.edit_btn').unbind('click').click(function(){
    var mch_sub_id=$(this).parent().siblings('.mch_sub_id').text(),
        _xsrf=$('input[name="_xsrf"]').val();
    checkSubUser(mch_sub_id,_xsrf,2);
    $('#send_sub_user').unbind('click').on('click',function(){
        var _html='';
        $.ajax({
            type : "post",  //提交方式
            url : sub_user_host+"/merchant/settings/sub_user/edit",//路径
            data : {
                "mch_sub_id" : mch_sub_id,
                "login_name" : $('#check_login').val(),
                "mch_sub_name" : $('#check_name').val(),
                "phone" : $('#check_phone').val(),
                "email" : $('#check_email').val(),
                "status" : $('#subUserSelect').val(),
                "_xsrf":_xsrf
            },//数据，这里使用的是Json格式进行传输
            success : function(result) {//返回数据根据结果进行相应的处理
                if ( result.code ==200 ) {
                    //$('#changeModal').modal('hide')
                    $(".addNew").after("<div class='newSuccess'>修改成功</div>");
                    $(".newSuccess").fadeIn(3000).delay(1000).fadeOut(2000);
                    setTimeout(function(){
                        window.location=sub_user_host+'/merchant/settings/sub_user';
                    },2000)
                } else {
                    for(i in result.data){
                        _html+='<p>'+result.data[i]+'</p>';
                    }
                    $('.change-error').html(_html);
                }
            }
        });
        if($('#subUserSelect').val() == 2){
           $.ajax({
               type : "get",  //提交方式
            url : sub_user_host+"/merchant/settings/sub_user/bindingstatus",//路径
            data : {
                "mch_sub_id" : mch_sub_id,
                "binding" : 2
            },
               success : function(result) {
                   if (result.code == 200 && result.msg == 2) {
                      window.location.reload();
            } else {
                       errorTipBtn(result.msg)

            }}
               }
           )
        }
    })
})

//新增员工账号
$('#add-mch-sub-user').unbind('click').on('click',function(){
    var _html='',_xsrf=$('input[name="_xsrf"]').val();
    $.ajax({
        type : "post",  //提交方式
        url : sub_user_host+"/merchant/settings/sub_user/add",//路径
        data : {
            "login_name" : $('#mch_sub_user_form input[name="login_name"]').val()+$('#mch_sub_user_form input[name="login_name"]').siblings('span').text(),
            "mch_sub_name" : $('#mch_sub_user_form input[name="mch_sub_name"]').val(),
            "phone" : $('#mch_sub_user_form input[name="phone"]').val(),
            "email" : $('#mch_sub_user_form input[name="email"]').val(),
            "status" : $('#mch_sub_user_form select').val(),
            "_xsrf":_xsrf
        },//数据，这里使用的是Json格式进行传输
        success : function(result) {//返回数据根据结果进行相应的处理
            if ( result.code ==200 ) {
                $(".addNew").after("<div class='newSuccess'>新增成功</div>");
                $(".newSuccess").fadeIn(3000).delay(1000).fadeOut(2000);
                setTimeout(function(){
                    window.location=sub_user_host+'/merchant/settings/sub_user';
                },2000)
            } else {
                for(i in result.data){
                    _html+='<p>'+result.data[i]+'</p>';
                }
                $('.change-error').html(_html);
            }
        }
    });
})
































