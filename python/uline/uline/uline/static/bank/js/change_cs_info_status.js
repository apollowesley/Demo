/**
 * Created by xiezhigang on 16/10/21.
 */
function authMchInletStatus(value) {
    // 状态为2 审核通过

    $('body').ulaiberLoading({loadingStatus:true});

    //商户id
    var tr = "#tr_" + value;
    $(tr).addClass('hover').siblings().removeClass('hover');
    $.ajax({
        type: 'GET',
        data: {"mch_id": value},
        dataType: 'json',
        url: '/bank/inlet/mch/auth',
        beforeSend: function (XMLHttpRequest) {
            // 请求前处理
        },
        success: function (res) {
            // 请求成功处理
            if(res.code==200 && res.msg=="fsuccess"){
                // $(tr + " td:nth-child(5)").html("未激活");
                $(tr + " td:nth-child(5)").html("复审中").append("<div class='passBox'>初审通过</div>");
                $(tr + " td:nth-child(6)").html("");
                $(".passBox").delay(1000).fadeOut();
                setTimeout(function(){
                    openNewTable(value,1);
                },1000);

            }
            else if(res.code==200 && res.msg=="csuccess"){
                // $(tr + " td:nth-child(5)").html("未激活");
                $(tr + " td:nth-child(5)").html("审核通过").append("<div class='passBox'>复审通过</div>");
                $(tr + " td:nth-child(6)").html("");
                $(".passBox").delay(1000).fadeOut();
                setTimeout(function(){
                    openNewTable(value,1,true);
                },1000);

            }
            else if(res.code==200 && res.msg=="success"){

                // $(tr + " td:nth-child(5)").html("未激活");
                $(tr + " td:nth-child(5)").html("审核通过").append("<div class='passBox'>审核通过</div>");
                $(tr + " td:nth-child(6)").html("");
                $(".passBox").delay(1000).fadeOut();
                setTimeout(function(){
                    judgeStatus(value);
                    openNewTable(value,1,true);
                },1000);

            }
            else if(res.code==200 && res.msg=="inleting"){

                // $(tr + " td:nth-child(5)").html("未激活");
                $(tr + " td:nth-child(5)").html("进件中").append("<div class='passBox'>进件中</div>");
                $(tr + " td:nth-child(6)").html("");
                $(".passBox").delay(1000).fadeOut();
                setTimeout(function(){
                    judgeStatus(value);
                    openNewTable(value,1,true);
                },1000);

            }
            else if(res.code==406 && res.msg=="进件到支付宝或微信失败"){
                $(tr + " td:nth-child(4)").html("未激活");
                $(tr + " td:nth-child(5)").html("审核不通过").append("<div class='passBox'>进件到微信或支付宝失败,系统已自动驳回</div>");
                $(tr + " td:nth-child(6)").html("");
                $(".passBox").delay(1000).fadeOut();
                setTimeout(function(){
                    openNewTable(value,1);
                },1000);

            } else {
                // alert(res.msg)
                errorTipBtn(res.msg)

            }
        },
        complete: function (XMLHttpRequest, textStatus) {
            // 完成请求处理
            $('body').ulaiberLoading({loadingStatus:false});
        },
        error: function () {
            $('body').ulaiberLoading({loadingStatus:false});
            // 请求出错处理
            $(tr + " td:nth-child(5)").append("<div class='passBox'>操作失败</div>");
            $(".passBox").delay(1000).fadeOut(2000);
        }
    });
    var e = window.event
    if(e.stopPropagation()){
        e.stopPropagation();
    } else {
        e.cancelBubble = true;
    }
}
function denyMchInletStatus(value) {
    // todo 驳回操作会有弹窗录入驳回原因
    // 状态为3 驳回

    //商户id
    var tr = "#tr_" + value;
    var input = 'turnDownInpt_' + String(value)
    var comment = document.getElementById(input).value;
    $.ajax({
        type: 'GET',
        data: {"mch_id": value, "comment": comment},
        dataType: 'json',
        url: '/bank/inlet/mch/deny',
        beforeSend: function (XMLHttpRequest) {
            // 请求前处理
        },
        success: function (res) {
            // 请求成功处理
            if(res.code==200){
                $(tr + " td:nth-child(5)").html("审核不通过").append("<div class='passBox'>已驳回</div>");
                $(tr + " td:nth-child(6)").children("a").remove();
                $('.modal').modal('hide');
                $(".passBox").delay(1000).fadeOut();
                setTimeout(function(){
                    openNewTable(value,1);
                },1000);
            } else {
                errorTipBtn(res.msg)
            }
        },
        complete: function (XMLHttpRequest, textStatus) {
            // 完成请求处理
        },
        error: function () {
            // 请求出错处理
            $(tr + " td:nth-child(5)").append("<div class='passBox'>操作失败</div>");
            $(".passBox").delay(1000).fadeOut(2000);
        }
    });
    var e = window.event;
    if(e.stopPropagation()){
        e.stopPropagation();
    } else {
        e.cancelBubble = true;
    }
}
function judgeStatus(value){
    $.ajax({
        type: 'GET',
        data: {"mch_id": value},
        dataType: 'json',
        url: '/bank/inlet/cs/detail',
        beforeSend: function (XMLHttpRequest) {
            // 请求前处理
        },
        success: function (res) {
            // 请求成功处理
            if(res.code==200){
                for (var index = 0; index < res.data.payment.length; index++) {
                    if(res.data.payment[index].activated_status==2){
                        $("#tr_"+value + " td:nth-child(4)").html("已激活");
                        return;
                    }
                }
                $("#tr_"+value + " td:nth-child(4)").html("未激活");
            }
        }

    });
};