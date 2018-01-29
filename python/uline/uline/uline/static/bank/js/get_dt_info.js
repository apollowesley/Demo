/**
 * Created by xiezhigang on 16/10/17.
 */
tableBox = $("#dtPayInfo");
appendPayHtml = "";
appendMchInfoHtml = "";
function openNewTable(value,_status) {
    var trStatus=$("#tr_"+value).attr('datashow');
    if(_status=='1'&&trStatus=='true'){
        $("#tr_"+value).attr('datashow','true');
        $("#tr_"+value).siblings().attr('datashow','false');
    } else if (trStatus!=='true') {
        $("#tr_"+value).attr('datashow','true');
        $("#tr_"+value).siblings().attr('datashow','false');

    }else{
        return;
    }
    loadingShow();
    if (document.getElementById("tabs")){
        appendPayHtml = "";
        appendMchInfoHtml = "";
    }
    $.ajax({
        type: 'GET',
        data: {"dt_id": value},
        dataType: 'json',
        url: '/bank/inlet/dt/detail'
    }).done(function(res){
        loadingHide();
        if (res.code == '200') {
            var data = res.data;
            var wx = "", wx_ind_code="", industry_name="";
            if (data.wx_sub_mch_id) {
                wx = data.wx_sub_mch_id;
                wx_ind_code = data.wx_ind_code;
                industry_name = data.industry_name
            } else {
                wx = "无";
                wx_ind_code="无";
                industry_name="无";
            }
            var appendHtml = "";
            var payHtml = "";
            var authHtml = "";
            var activateHtml = "";

            var payTypeName = "";
            var activatedName = "";
            var checkItem1 = "";
            var checkItem2 = "";
            var checkItem3 = "";
            var checkItem4 = "";
            var checkItem5 = "";
            var checkItem7 = "";
            var checkItem8 = "";
            var checkItem9 = "";
            var bt_name = "";
            var activatedHtml = "";
            var activatedBatchHtml = "";
            var paymentTypeArr = [];
            var payOperateArr = [];

            var licenseNum = "";
            var licenseStartDate = "";
            var licenseEndDate = "";
            var licensePeriod = "";
            var licenseScope = "";
            var licenseImgOld = data.license_img;

            if(data.balance_type==1){
                bt_name = '企业';
            }else if(data.balance_type==2){
                bt_name = '个人';
            }

            for (var payIndex = 0; payIndex < data.payment.length; payIndex++) {
                paymentTypeArr[payIndex] = data.payment[payIndex].activated_status;
                payOperateArr[payIndex] = data.payment[payIndex].operate;
            }
            activatedBatchHtml+="<div class='col-md-12 col-sm-12' id='activated_batch'>";
            if(data.bk_id==1) {
                for (var arrIndex = 0; arrIndex < paymentTypeArr.length; arrIndex++) {
                    if (data.auth_status == 2 && paymentTypeArr[arrIndex] == 1  && payOperateArr[arrIndex]==1) {
                        activatedBatchHtml = activatedBatchHtml + "<a href='javascript:void(0);' onclick='activatedBatchDtInletStatus(" + data.dt_id + ")'>激活全部</a>";
                        break;
                    }
                }
                for (var arrIndex = 0; arrIndex < paymentTypeArr.length; arrIndex++) {
                    if (paymentTypeArr[arrIndex] == 2 && payOperateArr[arrIndex]==1) {
                        var url = '/bank/inlet/dt/batchClose';
                        activatedBatchHtml = activatedBatchHtml + "<a style='margin-left:15px;' href='javascript:void(0);' onclick=rateCloseAll('" + url + "'," + data.dt_id + ")>关闭全部</a>";
                        break;
                    }
                }
            }
            activatedBatchHtml+="</div>";
            var status_index=0;


            // 有效的支付方式
            var AVAILABLE_PAYMENTS = {
                //微信线下支付
                'WX_OFFLINE_NATIVE': '微信-扫码支付（线下D1）',
                'WX_OFFLINE_MICROPAY': '微信-刷卡支付（线下D1）',
                'WX_OFFLINE_JSAPI': '微信-公众账号支付（线下D1）',

                //微信线上支付
                'WX_ONLINE_NATIVE': '微信-扫码支付（线上D1）',
                'WX_ONLINE_JSAPI': '微信-公众账号支付（线上D1）',
                'WX_ONLINE_APP': '微信-APP支付（线上D1）',
                'WX_ONLINE_MWEB': '微信-H5支付（线上D1）',

                // 微信围餐
                'WX_DINE_NATIVE': '微信-扫码支付（围餐）',
                'WX_DINE_MICROPAY': '微信-刷卡支付（围餐）',
                'WX_DINE_JSAPI': '微信-公众账号支付（围餐）',

                // 微信零费率
                'WX_ZERO_NATIVE': '微信-扫码支付（零费率）',
                'WX_ZERO_MICROPAY': '微信-刷卡支付（零费率）',
                'WX_ZERO_JSAPI': '微信-公众账号支付（零费率）',

                // 支付宝线下
                'ALI_OFFLINE_NATIVE': '支付宝-扫码支付（线下D1）',
                'ALI_OFFLINE_MICROPAY': '支付宝-刷卡支付（线下D1）',
                'ALI_OFFLINE_JSAPI': '支付宝-JS支付（线下D1）',


                // 银联
                'UNIONPAY_OFFLINE_JSAPI': '银联-JS支付费率',

                // d0 (临时，后期将删除)
                //微信线下支付
                'WX_OFFLINE_NATIVE_D0': '微信-扫码支付（线下D1）',
                'WX_OFFLINE_MICROPAY_D0': '微信-刷卡支付（线下D1）',
                'WX_OFFLINE_JSAPI_D0': '微信-公众账号支付（线下D1）',

                //微信线上支付
                'WX_ONLINE_NATIVE_D0': '微信-扫码支付（线上D1）',
                'WX_ONLINE_JSAPI_D0': '微信-公众账号支付（线上D1）',
                'WX_ONLINE_APP_D0': '微信-APP支付（线上D1）',
                'WX_ONLINE_MWEB_D0': '微信-H5支付（线上D1）',

                // 支付宝线下
                'ALI_OFFLINE_NATIVE_D0': '支付宝-扫码支付（线下D1）',
                'ALI_OFFLINE_MICROPAY_D0': '支付宝-刷卡支付（线下D1）',
                'ALI_OFFLINE_JSAPI_D0': '支付宝-JS支付（线下D1）',

                // 京东支付线下
                'JD_OFFLINE_NATIVE': '京东-扫码支付（T1）',
                'JD_OFFLINE_MICROPAY': '京东-刷卡支付（T1）',
                'JD_OFFLINE_JSAPI': '京东-JS支付（T1）',
                'JD_ONLINE_H5': '京东-H5支付（T1）',
                'JD_ONLINE_H5_DEBIT': '京东-H5支付（借记卡）（T1）',
            };
            var activatedHtml='';
            for(var i=0;i<data.payment.length;i++){
                for( _key in AVAILABLE_PAYMENTS){
                    if(data.payment[i].uline_payment_code == _key){
                        payHtml+='<div class="col-md-5 col-sm-5" style="text-align:left;padding-left:10px;">'+AVAILABLE_PAYMENTS[_key]+'</div><div class="col-md-3 col-sm-3">'+data.payment[i].settle_rate+'‰ </div>';
                        if (data.auth_status==2 && (data.payment[i].activated_status == 1 || data.payment[i].activated_status==3)) {
                            activatedName = '未激活';
                            if(data.bk_id==1 && data.payment[i].operate==1) {
                                activatedHtml = "<a href='javascript:;' id=" + "td_" + data.payment[i].pay_type + " onclick=activatedDtInletStatus(" + data.dt_id + ",'" + data.payment[i].uline_payment_code + "')>激活</a >"
                            }else{
                                activatedHtml = '';
                            }
                        }else if(data.payment[i].activated_status==2){
                            status_index++;
                            activatedName = '激活状态';
                            var data_url='/bank/inlet/dt/close';
                            if(data.bk_id==1) {
                                activatedHtml = "<a href='javascript:;' onclick=rateClose('" + data_url + "'," + data.dt_id + ",'" + data.payment[i].uline_payment_code + "','" + payTypeName + "')>关闭</a >"
                            }
                        }else if(data.payment[i].activated_status==3){
                            status_index++;
                            activatedName = '修改中';
                            activatedHtml = '';
                        }else {
                            activatedName = '未激活';
                            activatedHtml = '';
                        }
                        payHtml+='<div class="col-md-2 col-sm-2">'+activatedName+'</div>';
                        payHtml+='<div class="col-md-2 col-sm-2">'+activatedHtml+'</div>';
                    }
                }
            }
            if(status_index == 0){
                $("#tr_"+value).children().eq(2).html('未激活');
            }

            var roleHtml=''
            if(!$.isEmptyObject(data.role)){
                if(data.role.wx_draw_rate != null){
                    roleHtml+='<div class="role-box col-md-12">微信支付D0垫资费率： '+data.role.wx_draw_rate+' ‰</div>';
                }
                if(data.role.wx_draw_fee != null){
                    roleHtml+='<div class="role-box col-md-12">微信支付D0代付费用： '+data.role.wx_draw_fee+' 元/笔</div>';
                }
                if(data.role.ali_draw_rate != null){
                    roleHtml+='<div class="role-box col-md-12">支 付 宝 D0垫资费率： '+data.role.ali_draw_rate+' ‰</div>';
                }
                if(data.role.ali_draw_fee != null){
                    roleHtml+='<div class="role-box col-md-12">支 付 宝 D0代付费用： '+data.role.ali_draw_fee+' 元/笔</div>';
                }
            }

            appendHtml = appendHtml + "<div class='row zfBox' id='tabs'>";
            appendHtml = appendHtml + "<span>";
            appendHtml = appendHtml + "<ul class='col-md-12 col-sm-12'>";
            appendHtml = appendHtml + "<li class='col-md-6 col-sm-6 leftLine' id='payType' onclick='openPayTab()'>支付类型</li>";
            appendHtml = appendHtml + "<li class='col-md-6 col-sm-6' id='mchType' onclick='openMchTab()'>渠道信息</li>";
            appendHtml = appendHtml + "</ul>";
            appendHtml = appendHtml + "</span>";

            appendPayHtml = appendPayHtml + appendHtml;
            appendPayHtml = appendPayHtml + "<span id='payRate'>";
            appendPayHtml = appendPayHtml + "<div class='col-md-12 col-sm-12'>";
            appendPayHtml = appendPayHtml + "<div class='col-md-5 col-sm-5'>" + data.dt_name + "</div>";
            appendPayHtml = appendPayHtml + "<div class='col-md-3 col-sm-3'>费率</div>";
            appendPayHtml = appendPayHtml + "<div class='col-md-2 col-sm-2'>状态</div>";
            appendPayHtml = appendPayHtml + "<div class='col-md-2 col-sm-2'>操作</div>";
            appendPayHtml = appendPayHtml + "</div>";
            appendPayHtml = appendPayHtml + "<span>";
            appendPayHtml = appendPayHtml + payHtml;
            appendPayHtml = appendPayHtml + "</span>";
            appendPayHtml = appendPayHtml + "<span>";
            appendPayHtml = appendPayHtml + activatedBatchHtml;
            appendPayHtml = appendPayHtml + "</span>";
            appendPayHtml = appendPayHtml + "<span>";
            appendPayHtml = appendPayHtml + roleHtml;
            appendPayHtml = appendPayHtml + "</span>";
            appendPayHtml = appendPayHtml + "</span>";
            appendPayHtml = appendPayHtml + "</div>";

            data.auth_info.sort(valueSort('desc', 'auth_at'));
            for (var auth_index=0; auth_index < data.auth_info.length; auth_index++){
                if (data.auth_info[auth_index].auth_status == 3 || data.auth_info[auth_index].auth_status == 7) {
                    var target_index=  'auth_' + auth_index;
                    authHtml = authHtml + "<div><span>" + data.auth_info[auth_index].auth_at + "<a data-toggle='modal' data-target=" + "#" + target_index  +  ">" + data.auth_info[auth_index].comment + "</a> " + data.auth_info[auth_index].auth_user + "</span></div>";

                    //查看驳回原因弹框
                    authHtml = authHtml + '<div class="modal fade" id='+ target_index  + ' tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">'
                    authHtml = authHtml + '<div class="modal-dialog">'
                    authHtml = authHtml + '<div class="modal-content">'
                    authHtml = authHtml + '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4 class="modal-title" id="myModalLabel">驳回原因</h4></div>'
                    authHtml = authHtml + '<div class="modal-body"><div>' + data.auth_info[auth_index].auth_comment + '</div></div>'
                    authHtml = authHtml + '</div>'
                    authHtml = authHtml + '</div>'
                    authHtml = authHtml + '</div>'

                } else {
                    authHtml = authHtml + "<div><span>" + data.auth_info[auth_index].auth_at + " " + data.auth_info[auth_index].comment + " " + data.auth_info[auth_index].auth_user + "</span></div>";
                }

            }

            data.activated_info.sort(valueSort('desc', 'activated_at'));
            for(var i=0;i<data.activated_info.length;i++){
                for( _key in AVAILABLE_PAYMENTS){
                    if(data.activated_info[i].uline_payment_code == _key){
                        activateHtml = activateHtml + "<div><span>" + data.activated_info[i].activated_at + " " + AVAILABLE_PAYMENTS[_key] + " " + data.activated_info[i].comment + " " + data.activated_info[i].activated_user + "</span></div>";
                    }
                }
            }

            appendMchInfoHtml = appendHtml + "<span id='mchInfo'>";
            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>基本信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>渠道编号"
            if (data.rate == 1){
                appendMchInfoHtml = appendMchInfoHtml + "(0费率)";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</label><span>" + data.dt_id + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>微信商户编号</label><span>" + wx + "</span></div>";
            if(res.INTER_BANK){
                if(data.bk_type == 1){
                    appendMchInfoHtml = appendMchInfoHtml + "<div><label>所属银行</label><span>主银行</span></div>";
                }else if(data.bk_type == 2){
                    appendMchInfoHtml = appendMchInfoHtml + "<div><label>所属银行</label><span>" + data.bk_name + "</span></div>";
                }
            }
            if(data.unionpay_id){
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>银联机构号</label><span>"+data.unionpay_id+"</span></div>";
            }
            if(data.alipay_pid){
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>支付宝PID</label><span>"+data.alipay_pid+"</span></div>";
            }else{
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>支付宝PID</label><span></span></div>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>联系信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系人</label><span>" + data.contact +"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>手机号码</label><span>" + data.mobile + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>电子邮箱</label><span>" + data.email +"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>经营信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>经营类目</label><span>"+ data.u_ind_name +"</span></div>";
            //appendMchInfoHtml = appendMchInfoHtml + "<div><label>微信经营类目ID</label><span>"+ data.wx_ind_code +"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>微信经营类目</label><span>"+ data.wx_ind_name +"</span></div>";
            if (data.service_phone == null) {
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>客服电话</label><span>" + data.mobile + "</span></div>";
            } else {
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>客服电话</label><span>" + data.service_phone + "</span></div>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>渠道基本信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>渠道名称</label><span>"+data.dt_name+"</span></div>";
            if(data.district == undefined){
                data.district='';
            }
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>省份城市</label><span>"+ data.province + data.city +  data.district + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系地址</label><span>" + data.address +"</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>商户负责人信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>身份证</label><span>" + data.id_card_no + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>身份证照片</label><span>";
            appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.id_card_img_f + "' target='_blank'><img src='" + data.id_card_img_f + "'/></a>";
            appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.id_card_img_b + "' target='_blank'><img src='" + data.id_card_img_b + "'/></a>";
            appendMchInfoHtml = appendMchInfoHtml + "</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>营业执照信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>营业执照注册号</label>";
            if (data.license_num) {
                appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.license_num + "</span>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>营业开始日期</label>";
            if (data.license_start_date) {
                appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.license_start_date + "</span>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>营业结束日期</label>";
            if (data.license_period && data.license_period === 2) {
                appendMchInfoHtml = appendMchInfoHtml + "<span>" + '长期' + "</span>";
            } else {
                if (data.license_period){
                    if (data.license_end_date){
                        appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.license_end_date + "</span>";
                    }
                }
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>营业范围</label>";
            if (data.license_scope) {
                appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.license_scope + "</span>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            if (data.license_img) {
                appendMchInfoHtml = appendMchInfoHtml + "<div>";
                appendMchInfoHtml = appendMchInfoHtml + "<label>营业执照照片</label>";
                appendMchInfoHtml = appendMchInfoHtml + "<span><a href='" + data.license_img + "' target='_blank'><img style='width: 100px;height: 100px' src='" + data.license_img + "'/></a></span>";
                appendMchInfoHtml = appendMchInfoHtml + "</div>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>结算信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算账号类型</label><span>" + bt_name + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算户名</label><span>" + data.balance_name + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算银行</label><span>" + data.bank_name + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算帐号</label><span>" + data.balance_account + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list_lost'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>操作记录</h4>"
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + authHtml;
            appendMchInfoHtml = appendMchInfoHtml + activateHtml;
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            if(data.activated_status==1){
                $("#tr_"+value).find('td').eq(2).text('未激活');
            }else if(data.activated_status==2){
                $("#tr_"+value).find('td').eq(2).text('已激活');
            }

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
    $('#payType').addClass('leftLine').siblings().removeClass('leftLine');
}
function openMchTab() {
    if (document.getElementById("payType") && document.getElementById("mchType") ){
        tableBox.html(appendMchInfoHtml);
    }
    $('#mchType').addClass('leftLine').siblings().removeClass('leftLine');
}
openPayTab();
openMchTab();

function activatedDtInletStatus(dt_id, pay_type) {
    // 激活支付方式
    $.ajax({
        type: 'GET',
        data: {"dt_id": dt_id, "pay_type": pay_type},
        dataType: 'json',
        url: '/bank/inlet/dt/activated',
        beforeSend: function (XMLHttpRequest) {
            // 请求前处理
            // $("#mch_activation").append("<div><img class='passImg' src='/static/common/image/loading.gif'/></div>")
        },
        success: function (res) {
            // 请求成功处理
            if(res.code==200){
                td = "#td_" + pay_type;
                act = "#act_"  + pay_type;
                $(td).html("");
                $(act).html("已激活");
                //id编号
                tr = "#tr_" + dt_id;
                $(tr + " td:nth-child(3)").html("已激活");
                errorTip('激活成功');
                setTimeout(function(){
                    openNewTable(dt_id,1);
                },2000);
            } else if(res.code==407) {
                errorTipBtn(res.msg)
            }else{
                errorTip('激活失败')
            }
        },
        complete: function (XMLHttpRequest, textStatus) {
            // 完成请求处理
            // $("#mch_activation").remove()

        },
        error: function () {
            // 请求出错处理
            $("#mch_activation").append("<div class='passBox'>操作失败</div>");
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


//激活全部
function activatedBatchDtInletStatus(dt_id) {
    // 激活支付方式
    $.ajax({
        type: 'GET',
        data: {"dt_id": dt_id},
        dataType: 'json',
        url: '/bank/inlet/dt/batchActivated',
        beforeSend: function (XMLHttpRequest) {
            // 请求前处理
            // $("#mch_activation").append("<div><img class='passImg' src='/static/common/image/loading.gif'/></div>")
        },
        success: function (res) {
            // 请求成功处理
            if(res.code==200){
                $("[id^=td_]").html("");
                $("[id^=act_]").html("已激活");
                $("#activated_batch").remove();

                //id编号
                tr = "#tr_" + dt_id;
                $(tr + " td:nth-child(3)").html("已激活");
                errorTip('激活成功');
                setTimeout(function(){
                    openNewTable(dt_id,1);
                },2000);
            }else if(res.code==407) {
                errorTipBtn(res.msg);
            }else{
                errorTip('激活失败')
            }
        },
        complete: function (XMLHttpRequest, textStatus) {
            // 完成请求处理
            // $("#mch_activation").remove()

        },
        error: function () {
            // 请求出错处理
            $("#mch_activation").append("<div class='passBox'>操作失败</div>");
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
