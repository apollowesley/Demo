/**
 * Created by xiezhigang on 16/10/17.
 */
tableBox = $("#dtPayInfo");
appendPayHtml = "";
appendMchInfoHtml = "";
function openNewTable(value) {
    if ($("#tr_"+value).attr('class') == "hover") {
        return;
    }
    appendPayHtml = "";
    appendMchInfoHtml = "";
    loadingShow();
    $.ajax({
        type: 'GET',
        data: {"dt_id": value},
        dataType: 'json',
        url: '/dist/inlet/dt/detail'
    }).done(function(res){
        loadingHide();
        if (res.code == '200') {
            var data = res.data;
            var appendHtml = "";
            var payHtml = "";
            var payTypeName = "";
            var activatedName = "";
            var checkItem1 = "";
            var checkItem2 = "";
            var checkItem3 = "";
            var toUrl = "";
            for (var index = 0; index < data.payment.length; index++) {
                if(data.payment[index].pay_type==1){
                    payTypeName = '微信－扫码支付';
                    checkItem1 = data.payment[index].pay_rate;
                }else if(data.payment[index].pay_type==2){
                    payTypeName = '微信－刷卡支付';
                    checkItem2 = data.payment[index].pay_rate;
                }else if(data.payment[index].pay_type==3){
                    payTypeName = '微信－公众账号支付';
                    checkItem3 = data.payment[index].pay_rate;
                }

                if(data.payment[index].activated_status==2){
                    activatedName = '激活状态';
                }else if(data.payment[index].activated_status==3){
                    activatedName = '修改中';
                }else {
                    activatedName = '未激活';
                }

                if(data.balance_type==1){
                    bt_name = '企业';
                }else if(data.balance_type==2){
                    bt_name = '个人';
                }
                payHtml = payHtml + "<div class='col-md-8 col-sm-8'>" + payTypeName +"</div>";
                payHtml = payHtml + "<div class='col-md-2 col-sm-2'>" + data.payment[index].pay_rate + "‰ </div>";
                payHtml = payHtml + "<div class='col-md-2 col-sm-2'>" + activatedName + "</div>"
            }

            appendHtml = appendHtml + "<div class='row zfBox' id='tabs'>";
            appendHtml = appendHtml + "<span>";
            appendHtml = appendHtml + "<ul class='col-md-12 col-sm-12'>";
            appendHtml = appendHtml + "<li class='col-md-6 col-sm-6 rightLine' id='payType' onclick='openPayTab()'>支付类型</li>";
            appendHtml = appendHtml + "<li class='col-md-6 col-sm-6 leftLine' id='mchType' onclick='openMchTab()'>商户信息</li>";
            appendHtml = appendHtml + "</ul>";
            appendHtml = appendHtml + "</span>";

            appendPayHtml = appendPayHtml + appendHtml;
            appendPayHtml = appendPayHtml + "<span id='payRate'>";
            appendPayHtml = appendPayHtml + "<div class='col-md-12 col-sm-12'>";
            appendPayHtml = appendPayHtml + "<div class='col-md-8 col-sm-8'>" + data.dt_name + "</div>";
            appendPayHtml = appendPayHtml + "<div class='col-md-2 col-sm-2'>费率</div>";
            appendPayHtml = appendPayHtml + "<div class='col-md-2 col-sm-2'>状态</div>";
            appendPayHtml = appendPayHtml + "</div>";
            appendPayHtml = appendPayHtml + "<span>";
            appendPayHtml = appendPayHtml + payHtml;
            appendPayHtml = appendPayHtml + "</span>";
            appendPayHtml = appendPayHtml + "</span>";
            appendPayHtml = appendPayHtml + "</div>";

            appendMchInfoHtml = appendHtml + "<span id='mchInfo'>";
            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>渠道编号:</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.dt_id + "</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>渠道名称:</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>"+data.dt_name+"</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>行业:</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>"+ data.industry_name +"</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>省份城市:</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>"+ data.province + data.city +"</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>联系地址:</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.address +"</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>联系人:</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.contact +"</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>联系电话:</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.mobile + "</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>电子邮箱:</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.email +"</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4 class='title'>结算账号类型:" + bt_name + "</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>结算户名:</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.balance_name + "</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>结算银行:</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.bank_name + "</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>结算帐号:</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.balance_account + "</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-6 col-sm-6'>";
            appendMchInfoHtml = appendMchInfoHtml + "<img src='" + data.id_card_img_f +"'/>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-6 col-sm-6'>";
            appendMchInfoHtml = appendMchInfoHtml + "<img src='" + data.id_card_img_b + "'/>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>身份证:</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.id_card_no + "</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div class='list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.auth_at+"</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<a class='btn btn-default btnTop' href="+toUrl+">修改</a>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            tableBox.html(appendPayHtml);
        } else {
            errorTip('请求超时，请稍后刷新页面重试');
        }
    }).fail(function (res,restext,response) {
        loadingHide();
        if(restext == 'abort'){
            $('body').ulaiberLoading({loadingText:'操作频繁，请稍后刷新页面重试'});
        }else{
            $('body').ulaiberLoading({loadingText:'请求超时，请稍后刷新页面重试'});
        }
    });
}
function openPayTab() {
    if (document.getElementById("payType") && document.getElementById("mchType")){
        tableBox.html(appendPayHtml);
    }
}
function openMchTab() {
    if (document.getElementById("payType") && document.getElementById("mchType")){
        tableBox.html(appendMchInfoHtml);
    }
}
openPayTab();
openMchTab();