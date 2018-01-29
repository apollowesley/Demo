/**
 * Created by liudachu on 30/3/17.
 */

// 加载loading  可调用以下方法
function loadingShow(){
    $('body').ulaiberLoading({});
}
function loadingHide(){
    $('body').ulaiberLoading({loadingStatus:false});
}

// 不带按钮定时隐藏提示弹窗  可调用以下方法
function errorTip(msg){
    $('body').ulaiberLoading({loadingText:msg});
}

// 带确定按钮隐藏提示弹窗  可调用以下方法
function errorTipBtn(msg){
    $('body').ulaiberLoading({loadingText:msg,loadingType:'pop'});
}




;(function($){
    $.fn.ulaiberLoading=function(options){
        var defaults={
            evenMask:true,       //遮罩
            evenParent:'body',   //定位的父级
            loadingStatus:true,   //loading是否显示
            loadingText:'',   //为提示语弹窗内容
            loadingType:'alert',   //loading是类型   alert:自动消失   pop:带一种按钮的操作提示   comfirm:确认or取消操作
            loadingTitle:'温馨提示', //默认头部标题
            sureBtn:'确认',
            cancelBtn:'取消',
            sureLink:'',    //确定按钮跳转地址
            cancelLink:'',  //取消按钮跳转地址
            sureFunction:function(){} ,//确定按钮回调操作
            cancelFunction:function(){} ,//取消按钮回调操作
        };
        var options=$.extend(defaults,options);
        var _html='<div class="ulaiber-box"><div class="ulaiber-mask"></div>';  //视图
        if(options.loadingText == ''){
            _html+='<div class="ulaiber-loading"></div>';
        }else{
            _html+='<div class="ulaiber-alert">' ;
            _html+='<div>' ;
            if(options.loadingType != 'alert'){
                _html+='<h3 class="ulaiber-alert-title">'+options.loadingTitle+'</h3>';
                _html+='<div class="ulaiber-btn">' ;
                _html+='<a class="sure-btn">'+options.sureBtn+'</a>' ;
                if(options.loadingType == 'comfirm'){
                    _html+='<a class="cancel-btn">'+options.cancelBtn+'</a>' ;
                }
                _html+='</div>' ;
            }
            _html+='<i class="close-btn">x</i>';
            _html+='<div class="ulaiber-alert-box">'+options.loadingText+'</div> ';
            _html+='</div>';
            _html+='</div>';
        }

        _html+='</div>';
        var isLoading=$('.ulaiber-box');
        if(options.loadingStatus){
            $('body').append(_html);
            if(options.loadingType == 'alert'){$('.ulaiber-alert').addClass('alert');}
        }else{
            isLoading.remove();
        }



        //定时关闭
        if(options.loadingType == 'alert' && options.loadingText != ''){
            setTimeout(function () {
                $('.ulaiber-box').remove();
            },2000);
        }

        //关闭按钮
        $('.close-btn').on('click',function(){
            $(this).parents('.ulaiber-box').remove();
        });

        //确定按钮 是否跳转页面
        $('.sure-btn').on('click', function () {
            if (options.sureLink != "" && options.sureLink != null) {
                window.location.href = options.sureLink;
            }else{
                $(this).parents('.ulaiber-box').remove();
                options.sureFunction();
            }
        });

        //取消按钮 是否跳转页面
        $('.cancel-btn').on('click', function () {
            if (options.cancelLink != "" && options.cancelLink != null) {
                window.location.href = options.cancelLink;
            }else{
                $(this).parents('.ulaiber-box').remove();
                options.cancelFunction();
            }
        });
    }
})(jQuery);



