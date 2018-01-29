/**
 * Created by base on 15/9/17.
 */
    $('.add-activity-btn').click(function(){
        $('#addActivity').modal('show');
        $('#addActivity').find('input').val('');
        $('#addActivity').find('.mch-name').html('无需填写，自动读取商户编号相关信息');
        $('#addActivity').find('.mch-shortname').html('无需填写，自动读取商户编号相关信息');
        $('.step-list li').removeClass('on');
        $('.pop-step-box').hide();
        $('.step-list li').eq(0).addClass('on');
        $('.pop-step-box').eq(0).show();
    });

    $('.first-btn').click(function(){
        var str=Trim($('[name="role_id"]').val());
        roleCheck(str,'one',$(this));
    });


    function getCookie(name) {
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    };
    function Trim(str){
        return str.replace(/(^\s*)|(\s*$)/g, "");
    }

    //第一步校验商户编号
    var keyStatus=true;
    var stepOneStatus=false;
    function roleCheck(str,step,that){
        $.ajax({
            headers: {"X-XSRFToken":getCookie("_xsrf")},
            type: 'get',
            dataType: 'json',
            data:{
                role_id:str
            },
            url: '/bank/subsidize/mch/mch_info',
            async:false,
            success: function (res) {
                $('.base-error-c').html('');
                keyStatus=true;
                loadingHide();
                if(res.code == 200){
                    stepOneStatus=true;
                    $('.mch-name').html(res.data.name);
                    $('.mch-shortname').html(res.data.shortname);
                    if(step=='one'){
                        loadingShow();
                        setTimeout(function(){
                            loadingHide();
                            that.parents('.pop-step-box').hide().next('.pop-step-box').show();
                            $('.step-list li').eq(1).addClass('on');
                        },500)

                    }
                }else{
                    $('.base-error-c').html(res.msg);
                    $('.mch-name').html('无需填写，自动读取商户编号相关信息');
                    $('.mch-shortname').html('无需填写，自动读取商户编号相关信息');
                }
            },
            error: function (xhr) {
                keyStatus=true;
                loadingHide();
                errorTip('请求失败，请稍后重试！');
            }

        });
    };
    $('[name="role_id"]').keyup(function(){
            var str=Trim($(this).val());
            if(!/^[0-9]*$/.test(str)){
                $('.base-error-c').html('请输入数字');
                return false;
            }
            if(str.length>=11 && keyStatus){
                keyStatus=false;
                roleCheck(str);
            }
        });


    //第二部新增活动商户
    $('[name="weixin"],[name="alipay"],.update-mch-weixin,.update-mch-alipay').keyup(function(){
        if($(this).val()>100){
            $(this).val('');
            errorTip('不能大于100');
            return;
        }else if($(this).val()<=0){
            $(this).val('');
            errorTip('不能小于等于0');
            return;
        }
    });
    $('.add-send-btn').click(function(){
        var that=$(this);
        loadingShow();
        var _params={
            role_id:$('[name="role_id"]').val(),
            weixin:$('[name="weixin"]').val(),
            alipay:$('[name="alipay"]').val()
        }
        $.ajax({
            headers: {"X-XSRFToken":getCookie("_xsrf")},
            type: 'POST',
            dataType: 'json',
            data:_params,
            url: '/bank/subsidize/mch/add',
            async:false,
            success: function (res) {
                loadingHide();
                if(res.code == 200){
                    that.parents('.pop-step-box').hide().next('.pop-step-box').show();
                    $('.step-list li').eq(2).addClass('on');
                }else{
                    errorTip(res.msg);
                }
            },
            error: function (xhr) {
                loadingHide();
                errorTip('请求失败，请稍后重试！');
            }

        });
    })

    //获取详情
    function getInfo(role_id,type,background){
        var _params={
            role_id:role_id
        };

        $.ajax({
            headers: {"X-XSRFToken":getCookie("_xsrf")},
            type: 'get',
            dataType: 'json',
            data:_params,
            url: '/'+background+'/subsidize/mch/detail',
            async:false,
            success: function (res) {
                loadingHide();
                if(res.code == 200){
                    if(type=='update'){
                        $('.update-mch-id').html(res.data.role_id);
                        $('.update-mch-name').html(res.data.role_name);
                        $('.update-mch-shortname').html(res.data.role_shortname);
                        $('.update-mch-status').val(res.data.valid);
                        $('.update-mch-weixin').val(res.data.rate.weixin);
                        $('.update-mch-alipay').val(res.data.rate.alipay);
                        $('#updateActivity').modal('show');
                    }else{
                        for(_key in res.data){
                            $('td[td-name="'+_key+'"]').html(res.data[_key]);
                        }
                        if(res.data.valid==2){
                            $('.table-valid').html('已停止')
                        }else if(res.data.valid==1){
                            $('.table-valid').html('参与中')
                        }
                        $('.table-weixin').html(res.data.rate.weixin+'%');
                        $('.table-alipay').html(res.data.rate.alipay+'%');

                        $('#activityInfo').modal('show');
                    }
                }else{
                    infoData={}
                    errorTip(res.msg);
                }
            },
            error: function (xhr) {
                infoData={}
                loadingHide();
                errorTip('请求失败，请稍后重试！');
            }

        });
    }

    //修改活动商户
    function updateActivity(){
        loadingShow();
        var _params={
            role_id:$('.update-mch-id').html(),
            status:$('.update-mch-status').val(),
            weixin:$('.update-mch-weixin').val(),
            alipay:$('.update-mch-alipay').val(),
        };
        $.ajax({
            headers: {"X-XSRFToken":getCookie("_xsrf")},
            type: 'post',
            dataType: 'json',
            data:_params,
            url: '/bank/subsidize/mch/modify',
            async:false,
            success: function (res) {
                loadingHide();
                if(res.code == 200){
                    $('#updateActivity').modal('hide');
                    errorTip('修改成功');
                    setTimeout(function(){
                        window.location.reload();
                    },1500)
                }else{
                    errorTip(res.msg);
                }
            },
            error: function (xhr) {
                loadingHide();
                errorTip('请求失败，请稍后重试！');
            }

        });
    }