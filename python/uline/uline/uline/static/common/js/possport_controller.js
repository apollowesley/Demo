
;(function($){
    var sys_type_code='',
        token='',
        timer_status=true;

    var timerTxt=$('.login-input-btn');
    var type=getParams().type;
    if( type=='reset' || type=='first' ){
        $('.step-list-forget').hide();
        $('.step-list-reset').show();
        $('.step-box').eq(0).hide();
        $('.step-box').eq(1).show();
    }


    //获取cookie
    function getCookie(name) {
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    };

    //公用请求方法
    function ajaxResponsePromise(request_url,request_data,request_type){
        if(request_type == 'POST'){
            var xsrf=getCookie("_xsrf");
        }

        return $.ajax({
            headers: {"X-XSRFToken":xsrf},
            type:request_type || 'GET',
            url:request_url,
            data:request_data,
            dataType:'json',
        })
    }

    //解密参数
    function getParams() {
        var params = {};
        location.href.replace(/([\w-]+)\=([^\&\=]+)/ig, function (a, b, c) {
            params[b] = c;
        });

        for (var key in params) {
            params[key] = decodeURIComponent(params[key]);
        }
        return params;
    }

    var possportServices={
        'login':function(request_data){
            var params=request_data;
            var url='/account/login';
            return ajaxResponsePromise(url,params,'POST');
        },//登录接口
        'forgetVerifyName':function(request_data){
            var params=request_data;
            var url='/account/forgetpwd';
            return ajaxResponsePromise(url,params,'POST');
        },//忘记密码--验证账号
        'forgetGetCode':function(request_data){
            var params=request_data;
            var url='/account/forgetpwd/auth/code';
            return ajaxResponsePromise(url,params);
        },//忘记密码--获取验证码
        'forgetVerifyCode':function(request_data){
            var params=request_data;
            var url='/account/forgetpwd/auth';
            return ajaxResponsePromise(url,params,'POST');
        },//忘记密码--验证验证码
        'forgetVerifyPassword':function(request_data){
            var params=request_data;
            var url='/account/forgetpwd/modify';
            return ajaxResponsePromise(url,params,'POST');
        },//忘记密码--验证密码
        'firstGetCode':function(request_data){
            var params=request_data;
            var url='/account/login/code';
            return ajaxResponsePromise(url,params);
        },//第一次登录--获取验证码
        'firstVerifyCode':function(request_data){
            var params=request_data;
            var url='/account/login/auth';
            return ajaxResponsePromise(url,params,'POST');
        },//第一次登录--验证验证码
        'firstVerifyPassword':function(request_data){
            var params=request_data;
            var url='/account/login/modify';
            return ajaxResponsePromise(url,params,'POST');
        },//第一次登录--验证密码
        'resetGetCode':function(request_data){
            var params=request_data;
            var url='/account/resetpasswd/auth/code';
            return ajaxResponsePromise(url,params);
        },//重置密码--获取验证码
        'resetVerifyCode':function(request_data){
            var params=request_data;
            var url='/account/resetpasswd/auth';
            return ajaxResponsePromise(url,params,'POST');
        },//重置密码--验证验证码
        'resetVerifyPassword':function(request_data){
            var params=request_data;
            var url='/account/resetpasswd/modify';
            return ajaxResponsePromise(url,params,'POST');
        },//重置密码--验证密码
    };


    //click
    $(document).on('click','[data-click]',function(e) {
        e.stopPropagation();
        e.preventDefault();

        var self = $(this),
            name = $(this).data('click');

        switch (name) {

            case 'login-tip':
                $('.login-pop').slideDown();
                break;

            case 'login-tip-close':
                $('.login-pop').slideUp();
                break;

            case 'login':
                var _params={
                    login_name:$('input[name="login_name"]').val(),
                    password:$('input[name="password"]').val(),
                };
                if(_params.login_name==''){
                    $('.tip-error').html('账号不能为空');
                    return false;
                }else if(_params.password==''){
                    $('.tip-error').html('密码不能为空');
                    return false;
                }else if(_params.password.length<6){
                    $('.tip-error').html('密码长度不能少于6位');
                    return false;
                }
                $('.tip-error').html('');
                loadingShow();
                possportServices.login(_params).then(function(res){
                    loadingHide();
                    if(res.code==200){
                        window.location.href=res.url;
                    }else if(res.code==405){
                        //初次登录，修改密码
                        $('body').ulaiberLoading({loadingText:res.msg,loadingType:'pop',sureLink:'/account/forgetpwd?type=first'});
                    }else if(res.code==406){
                        $('.tip-error').html(res.msg);
                    }
                },function(){
                    loadingHide();
                    errorTip('请求失败，请稍后重试！');
                });
                break;

            case 'verifyName':
                var fnName=type+'VerifyName';
                var _params={
                    login_name:$('input[name="login_name"]').val(),
                };
                if(_params.login_name==''){
                    $('.tip-error').html('账号不能为空');
                    return false;
                }
                $('.tip-error').html('');
                loadingShow();
                possportServices[fnName](_params).then(function(res){
                    loadingHide();
                    if(res.code==200){
                        sys_type_code=res.sys_type_code;
                        token=res.token;
                        $('.step-list li').eq(1).addClass('on');
                        self.parents('.step-box').hide().next().show();
                    }else{
                        $('.tip-error').html(res.msg);
                    }
                },function(){
                    loadingHide();
                    errorTip('请求失败，请稍后重试！');
                });
                break;

            case 'getAuthCode':
                var fnName=type+'GetCode';
                if(!timer_status){
                    return false;
                }
                timer_status=false;
                var _params={
                    sys_type_code:sys_type_code,
                    token:token,
                };
                loadingShow();
                possportServices[fnName](_params).then(function(res){
                    loadingHide();
                    if(res.code==200){
                        $('.auth-code-tip').html('已发送验证码至：'+res.data);
                        timer(60);
                    }else{
                        timer_status=true;
                        timerTxt.html('重新获取验证码');
                        errorTip(res.msg);
                    }
                },function(){
                    timer_status=true;
                    timerTxt.html('重新获取验证码');
                    loadingHide();
                    errorTip('请求失败，请稍后重试！');
                });
                break;

            case 'verifyAuthCode':
                var fnName=type+'VerifyCode';
                var _params={
                    auth_code:$('input[name="auth_code"]').val(),
                    sys_type_code:sys_type_code,
                    token:token,
                };
                if(_params.auth_code==''){
                    $('.tip-error').html('验证码不能为空');
                    return false;
                }
                $('.tip-error').html('');
                loadingShow();
                possportServices[fnName](_params).then(function(res){
                    loadingHide();
                    if(res.code==200){
                        if(type=='forget'){
                            $('.step-list-forget li').eq(2).addClass('on');
                        }else if( type=='first' || type=='reset' ){
                            $('.step-list-reset li').eq(1).addClass('on');
                        }
                        self.parents('.step-box').hide().next().show();
                    }else{
                        $('.tip-error').html(res.msg);
                    }
                },function(){
                    loadingHide();
                    errorTip('请求失败，请稍后重试！');
                });
                break;

            case 'verifyPassword':
                var fnName=type+'VerifyPassword';
                var _params={
                    newPwd:$('input[name="newPwd"]').val(),
                    checkPwd:$('input[name="checkPwd"]').val(),
                    sys_type_code:sys_type_code,
                    token:token,
                };
                if(_params.newPwd!=_params.checkPwd){
                    $('.tip-error').html('两次密码不一致，请重新输入');
                    return false;
                }else if(_params.newPwd=='' || _params.checkPwd=='' ){
                    $('.tip-error').html('密码不能为空');
                    return false;
                }else if(_params.newPwd.length<6 || _params.checkPwd.length<6){
                    $('.tip-error').html('密码不能小于6位');
                    return false;
                }
                $('.tip-error').html('');
                loadingShow();
                possportServices[fnName](_params).then(function(res){
                    loadingHide();
                    if(res.code==200){
                        errorTip('修改成功,正在跳转登录页');
                        setTimeout(function(){
                            window.location.href='/account/'
                        },1000)
                    }else{
                        $('.tip-error').html(res.msg);
                    }
                },function(){
                    loadingHide();
                    errorTip('请求失败，请稍后重试！');
                });
                break;

        }
    });

    //倒计时
    function timer(num){
        if(num<=0){
            timerTxt.html('重新获取验证码');
            timer_status=true;
        }else{
            num--;
            timerTxt.html(num+' s');
            setTimeout(function () {
                timer(num)
            }, 1000)
        }
    }






})(jQuery);