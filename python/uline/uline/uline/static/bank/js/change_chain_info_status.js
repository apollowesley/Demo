/**
 * Created by xiezhigang on 16/10/21.
 */
function authDtInletStatus(value) {
    event.stopPropagation();
    $('body').ulaiberLoading({loadingStatus:true});
    // 状态为2 审核通过
    tr = "#tr_" + value;
    $(tr).addClass('hover').siblings().removeClass('hover');
    $.ajax({
        type: 'GET',
        data: {"dt_id": value},
        dataType: 'json',
        url: '/bank/inlet/chain/auth',
        beforeSend: function (XMLHttpRequest) {
            // 请求前处理
        },
        success: function (res) {
            // 请求成功处理
            if(res.code==200 && res.msg=="fsuccess"){
                // $(tr + " td:nth-child(3)").html("未激活");
                $(tr + " td:nth-child(6)").html("复审中");
                $(tr + " td:nth-child(7)").html("").append("<div class='passBox'>初审通过</div>");
                $(".passBox").delay(1000).fadeOut();
                setTimeout(function(){
                    openNewTable(value,1);
                },1000);
            }
            else if(res.code==200 && res.msg=="csuccess"){
                // $(tr + " td:nth-child(3)").html("未激活");
                $(tr + " td:nth-child(6)").html("审核通过");
                $(tr + " td:nth-child(7)").html("").append("<div class='passBox'>复审通过</div>");
                $(".passBox").delay(1000).fadeOut();
                setTimeout(function(){
                    openNewTable(value,1);
                },1000);
            }
            else if(res.code==200 && res.msg=="success"){
                // $(tr + " td:nth-child(3)").html("未激活");
                $(tr + " td:nth-child(6)").html("审核通过");
                $(tr + " td:nth-child(7)").html("").append("<div class='passBox'>审核通过</div>");
                $(".passBox").delay(1000).fadeOut();
                setTimeout(function(){
                    judgeStatus(value);
                    openNewTable(value,1);
                },1000);
            }
            else if(res.code==200 && res.msg=="inleting"){
                // $(tr + " td:nth-child(3)").html("未激活");
                $(tr + " td:nth-child(6)").html("进件中");
                $(tr + " td:nth-child(7)").html("").append("<div class='passBox'>进件中</div>");
                $(".passBox").delay(1000).fadeOut();
                setTimeout(function(){
                    judgeStatus(value);
                    openNewTable(value,1);
                },1000);
            }
            else if(res.code==406 && res.msg=="进件到微信失败"){
                $(tr + " td:nth-child(5)").html("未激活");
                $(tr + " td:nth-child(6)").html("审核不通过");
                $(tr + " td:nth-child(7)").html("").append("<div class='passBox' style='width: 300px'>进件到微信失败,系统已经自动驳回</div>");
                $(".passBox").delay(1000).fadeOut();
                setTimeout(function(){
                    openNewTable(value,1);
                },1000);
            }
            else if(res.code==407){
                $(tr + " td:nth-child(6)").html("审核不通过");
                $(tr + " td:nth-child(7)").html("");
                errorTipBtn(res.msg);
                setTimeout(function(){
                    openNewTable(value,1);
                },1000);
            }
            else{
                errorTipBtn(res.msg)
            }

        },
        complete: function (XMLHttpRequest, textStatus) {
            // 完成请求处理
            $('body').ulaiberLoading({loadingStatus:false});
        },
        error: function (res) {
            $('body').ulaiberLoading({loadingStatus:false});
            // 请求出错处理
            $(tr + " td:nth-child(7)").append("<div class='passBox'>操作失败</div>");
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
function denyDtInletStatus(value) {
    // todo 驳回操作会有弹窗录入驳回原因
    // 状态为3 驳回

    //商户ID
    tr = "#tr_" + value;
    var input = 'turnDownInpt_' + String(value);
    var comment = document.getElementById(input).value;
    $.ajax({
        type: 'GET',
        data: {"dt_id": value , "comment": comment},
        dataType: 'json',
        url: '/bank/inlet/dt/deny',
        beforeSend: function (XMLHttpRequest) {
            // 请求前处理
        },
        success: function (res) {
            // 请求成功处理
            if(res.code==200){
                $(tr + " td:nth-child(6)").html("审核不通过");
                $(tr + " td:nth-child(7)").children("a").remove();
                $('.modal').modal('hide');
                $(tr + " td:nth-child(7)").append("<div class='passBox'>审核驳回</div>");
                $(".passBox").delay(1000).fadeOut();
                setTimeout(function(){
                    openNewTable(value,1);
                },1000);
            }
        },
        complete: function (XMLHttpRequest, textStatus) {
            // 完成请求处理
        },
        error: function () {
            // 请求出错处理
            $(tr + " td:nth-child(7)").append("<div class='passBox'>操作失败</div>");
            $(".passBox").delay(1000).fadeOut(2000,function(){
                window.location.reload();
            });
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
        data: {"dt_id": value},
        dataType: 'json',
        url: '/bank/inlet/chain/detail',
        beforeSend: function (XMLHttpRequest) {
            // 请求前处理
        },
        success: function (res) {
            // 请求成功处理
            if(res.code==200){
                for (var index = 0; index < res.data.payment.length; index++) {
                    if(res.data.payment[index].activated_status==2){
                        $("#tr_"+value + " td:nth-child(5)").html("已激活");
                        return;
                    }
                }
                $("#tr_"+value + " td:nth-child(5)").html("未激活");
            }
        }

    });
};