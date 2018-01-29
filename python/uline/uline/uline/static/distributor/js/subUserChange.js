/**
 * Created by apple on 12/4/17.
 */

var sub_user_host=window.location.protocol + '//' + window.location.host;
function checkSubUser(dt_sub_id,_xsrf,_status){
    $.ajax({
        type : "get",  //提交方式
        url : sub_user_host+"/dist/sub_user/info",//路径
        data : {
            "dt_sub_id" : dt_sub_id,
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
                $('#check_name').val(result.data.dt_sub_name);
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

//查看员工账号
$('.check_btn').on('click',function(){
    var dt_sub_id=$(this).parent().siblings('.dt_sub_id').text(),
        _xsrf=$('input[name="_xsrf"]').val();
    $('.change-error').html('');
    checkSubUser(dt_sub_id,_xsrf,1);
})


//编辑员工账号
$('.edit_btn').unbind('click').click(function(){
    var dt_sub_id=$(this).parent().siblings('.dt_sub_id').text(),
        _xsrf=$('input[name="_xsrf"]').val();
    checkSubUser(dt_sub_id,_xsrf,2);
    $('#send_sub_user').unbind('click').on('click',function(){
        var _html='';
        $.ajax({
            type : "post",  //提交方式
            url : sub_user_host+"/dist/sub_user/edit",//路径
            data : {
                "dt_sub_id" : dt_sub_id,
                "login_name" : $('#check_login').val(),
                "dt_sub_name" : $('#check_name').val(),
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
                        window.location=sub_user_host+'/dist/sub_user/';
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
})

//新增员工账号
$('#add-sub-user').unbind('click').on('click',function(){
    var _html='',_xsrf=$('input[name="_xsrf"]').val();
    $.ajax({
        type : "post",  //提交方式
        url : sub_user_host+"/dist/sub_user/add",//路径
        data : {
            "login_name" : $('#sub_user_form input[name="login_name"]').val()+$('#sub_user_form input[name="login_name"]').siblings('span').text(),
            "dt_sub_name" : $('#sub_user_form input[name="dt_sub_name"]').val(),
            "phone" : $('#sub_user_form input[name="phone"]').val(),
            "email" : $('#sub_user_form input[name="email"]').val(),
            "status" : $('#sub_user_form select').val(),
            "_xsrf":_xsrf
        },//数据，这里使用的是Json格式进行传输
        success : function(result) {//返回数据根据结果进行相应的处理
            if ( result.code ==200 ) {
                $(".addNew").after("<div class='newSuccess'>新增成功</div>");
                $(".newSuccess").fadeIn(3000).delay(1000).fadeOut(2000);
                setTimeout(function(){
                    window.location=sub_user_host+'/dist/sub_user/';
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
































