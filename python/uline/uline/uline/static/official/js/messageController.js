/**
 * Created by base on 13/7/17.
 */
/**
 * Created by base on 13/7/17.
 */


var view  = window.location.pathname;
view=view.split('/')[3];

//输入内容验证
$('[name="message_content"]').keyup(function(){
   if($(this).val().length>0){
       $('.base-error-c').html('');
   }else if($(this).val().length>200){
       $('.base-error-c').html('请输入推送内容，不能为空');
   }
});


//http
var MessageServices={
    'SendMessage':function(request_data){
        var params=request_data;
        var url='/official/operations/message/send';
        return ajaxResponsePromise(url,params,'POST');
    },
    'GetMessageStatus':function(request_data){
        var params=request_data;
        var url='/official/operations/message/searchBySendId';
        return ajaxResponsePromise(url,params);
    },
};

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
};


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




;(function($){
    var timer;
    //click
    $(document).on('click','[data-click]',function(e) {
        e.stopPropagation();
        e.preventDefault();

        var self = $(this),
            name = $(this).data('click');

        switch (name) {

            case 'send': //关闭右侧详情操作
                if($('[name="message_content"]').val() == ''){
                    $('.base-error-c').html('请输入推送内容，不能为空');
                }else{
                    $('body').ulaiberLoading({
                        loadingType:'comfirm',
                        loadingTitle:'确认推送短信吗？',
                        loadingText:'<p class="text-left"><span class="base-error-c">短信发送到商户手机后无法撤回，</span>你还要继续吗？</p>',
                        sureFunction:function(){
                            MessageController.SendMessage();

                        }
                    });

                    return false;
                }
                break;
        }
    });


    var MessageController={
        SendMessage:function(){
            var _params={
                message_content:$('[name="message_content"]').val(),
                "_xsrf":getCookie("_xsrf")
            };
            loadingShow();
            MessageServices.SendMessage(_params).then(function(res){
                var sendNum=0;
                if(res.code==200){
                    timerGo(res.data.send_id,sendNum);
                }else{
                    errorTip(res.msg);
                }
            })
        },
        GetMessageStatus:function(send_id,sendNum){
            var _params={
                send_id:send_id
            };

            MessageServices.GetMessageStatus(_params).then(function(res){
                loadingHide();
                if(res.code==200){
                    if(sendNum>10){
                        clearInterval(timer);
                        $('.message-pop').fadeOut();
                        $('body').ulaiberLoading({
                            loadingType:'pop',
                            loadingTitle:'发送失败',
                            loadingText:'<p class="text-left">请联系开发人员排查原因</p>'
                        });
                        return false;
                    }
                    var sum=res.data.sended_count+res.data.need_send_count; //发送中条数
                    var barWidth=(res.data.sended_count/sum)*100+'%'; //进度条长度
                    $('.message-pop').fadeIn();
                    if(res.data.need_send_count==0){
                        clearInterval(timer);
                        $('.message-progress h3').html('发送成功');
                        $('.message-small').html('全部短信发送成功（'+res.data.sended_count+'/'+sum+'）');
                        setTimeout(function(){
                            $('.message-pop').fadeOut();
                            location.reload();
                        },1500);
                    }else{
                        $('.message-progress h3').html('正在发送');
                        $('.message-small').html('正在发送短信（'+res.data.sended_count+'/'+sum+'）');
                    }
                    $('.message-progress-bar span').css({width:barWidth});
                }
            })
        }
    };

    function timerGo(send_id,sendNum){
        sendNum=sendNum;
        timer=setInterval(function(){
            sendNum++;
            MessageController.GetMessageStatus(send_id,sendNum);
        },1000);
    }

    //tab
    $('.tab-nav li').click(function(){
        var index=$(this).index();
        $.cookie('messageIndex',index);
        $(this).addClass('on').siblings().removeClass('on');
        $('.tab-content').eq(index).show().siblings('.tab-content').hide();
    });
    if($.cookie('messageIndex')==1){
        $('.tab-nav li').eq(1).addClass('on').siblings().removeClass('on');
        $('.tab-content').eq(1).show().siblings('.tab-content').hide();
    }


})(jQuery);














