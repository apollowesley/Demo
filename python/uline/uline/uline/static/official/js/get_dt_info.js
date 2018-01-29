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
    if (document.getElementById("tabs")) {
        appendPayHtml = "";
        appendMchInfoHtml = "";
    }
    loadingShow();
    $.ajax({
        type: 'GET',
        data: {"dt_id": value},
        dataType: 'json',
        url: '/official/inlet/dt/detail'
    }).done(function (res) {
        loadingHide();
        if (res.code == '200') {
            var data = res.data;
            var wx = "", wx_ind_code = "", industry_name = "";
            if (data.wx_sub_mch_id) {
                wx = data.wx_sub_mch_id;
                wx_ind_code = data.wx_ind_code;
                industry_name = data.industry_name
            } else {
                wx = "无";
                wx_ind_code = "无";
                industry_name = "无";
            }
            var imgCardFrontOld = data.id_card_img_f;
            var imgCardBackOld = data.id_card_img_b;
            var appendHtml = "";
            var payHtml = "";
            var authHtml = "";
            var modifyHtml = "";
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
            var checkItem21 = "";
            var checkItem22 = "";
            var checkItem23 = "";
            var checkItem101 = "";
            var checkItem102 = "";
            var checkItem103 = "";
            var checkItem104 = "";
            var checkItem105 = "";
            var checkItem107 = "";
            var checkItem108 = "";
            var checkItem109 = "";
            var toUrl = "";
            var bt_name = "";
            var licenseNum = "";
            var licenseStartDate = "";
            var licenseEndDate = "";
            var licensePeriod = "";
            var licenseScope = "";
            var licenseImgOld = data.license_img;
            var paymentStr="";
            var use_dine=0;

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

            if (data.balance_type == 1) {
                bt_name = '企业';
            } else if (data.balance_type == 2) {
                bt_name = '个人';
            }

            var payUrl='';
            for(var i=0;i<data.payment.length;i++){
                if(data.payment[i].uline_payment_code.indexOf('WX_DINE')>=0){
                    use_dine=1;
                }
                for( _key in AVAILABLE_PAYMENTS){
                    if(data.payment[i].uline_payment_code == _key){
                        payHtml+='<div class="col-md-6 col-sm-6" style="text-align:left;padding-left:10px;">'+AVAILABLE_PAYMENTS[_key]+'</div><div class="col-md-4 col-sm-4">'+data.payment[i].settle_rate+'‰ </div>';
                        if (data.payment[i].activated_status == 1) {
                            activatedName = '未激活';
                        } else if (data.payment[i].activated_status == 2) {
                            activatedName = '激活状态';
                        } else if (data.payment[i].activated_status == 3) {
                            activatedName = '修改中';
                        }
                        payHtml+='<div class="col-md-2 col-sm-2">'+activatedName+'</div>';
                    }
                }
                payUrl+='&'+data.payment[i].uline_payment_code+'='+data.payment[i].settle_rate;
            }

            var u_ind_name=data.u_ind_name.split('-');

            if (data.auth_status == 2 || data.auth_status == 3) {
                toUrl = '/official/inlet/dt/modify?dt_id=' + data.dt_id + '&email=' + data.email
                    + '&province=' + data.province + '&city=' + data.city + '&contact=' + data.contact
                    + '&mobile=' + data.mobile + '&balanceType=' + data.balance_type + '&bankNo=' + data.bank_no
                    + '&balanceNo=' + data.balance_account
                    + '&imgCardFrontOld=' + imgCardFrontOld
                    + '&imgCardBackOld=' + imgCardBackOld + '&area=' + u_ind_name[0]+ '&cmbProvince=' + u_ind_name[1]
                    + '&cmbCity=' + u_ind_name[2] + '&cmbArea=' + u_ind_name[3]+ '&dtType=' + data.dt_type+ '&use_dine=' + use_dine
                    + payUrl;
                    //+ '&address=' + data.address
                    //+ '&idCard=' + data.id_card_no
                    // + '&bankName=' + data.bank_name

                for(roleKey in data.role){
                    toUrl+='&'+roleKey+'='+data.role[roleKey];
                }
                if(data.wx_channel_id != ''){
                    toUrl += '&wxChannelId=' + data.wx_channel_id;
                }
                if(data.wx_app_channel_id != ''){
                    toUrl += '&wxAppChannelId=' + data.wx_app_channel_id;
                }
                if(data.bk_type){
                    toUrl += '&bk_type=' + data.bk_type;
                }
                if(data.bk_name){
                    toUrl += '&bk_name=' + data.bk_name;
                }

                // +'&licenseNum='+data.license_num
                // +'&licenseStartDate='+data.license_start_date
                // +'&licenseEndDate='+data.license_end_date
                // +'&licensePeriod='+data.license_period
                // +'&licenseScope='+data.license_scope
                // +'&licenseImgOld='+licenseImgOld;

                if (data.service_phone == null) {
                    toUrl += '&servicePhone=' + data.mobile;
                } else {
                    toUrl += '&servicePhone=' + data.service_phone;
                }

                if (data.license_num) {
                    toUrl += '&licenseNum=' + data.license_num;
                }
                if (data.license_start_date) {
                    toUrl += '&licenseStartDate=' + data.license_start_date;
                }
                if (data.license_end_date) {
                    toUrl += '&licenseEndDate=' + data.license_end_date;
                }
                if (data.license_period) {
                    toUrl += '&licensePeriod=' + data.license_period;
                }
                if(data.district != null){
                    toUrl += '&district=' + data.district;
                }
                /*if (data.license_scope) {
                    toUrl += '&licenseScope=' + data.license_scope;
                }*/
                if(data.unionpay_id){
                    toUrl += '&unionpay_id=' + data.unionpay_id;
                }
                if(data.alipay_pid){
                    toUrl += '&alipay_pid=' + data.alipay_pid;
                }
                toUrl += '&licenseImgOld=' + data.license_img;
                modifyHtml = modifyHtml + "<a class='btn btn-default btnTop'  onclick=setRateCookie('"+paymentStr+"') href=" + toUrl + ">修改</a>";
            }
            if(!$.isEmptyObject(data.role)){
                if(data.role.wx_draw_rate != null){
                    payHtml+='<div class="role-box col-md-12">微信支付D0垫资费率： '+data.role.wx_draw_rate+' ‰</div>';
                }
                if(data.role.wx_draw_fee != null){
                    payHtml+='<div class="role-box col-md-12">微信支付D0代付费用： '+data.role.wx_draw_fee+' 元/笔</div>';
                }
                if(data.role.ali_draw_rate != null){
                    payHtml+='<div class="role-box col-md-12">支 付 宝 D0垫资费率： '+data.role.ali_draw_rate+' ‰</div>';
                }
                if(data.role.ali_draw_fee != null){
                    payHtml+='<div class="role-box col-md-12">支 付 宝 D0代付费用： '+data.role.ali_draw_fee+' 元/笔</div>';
                }
            }


            appendHtml = appendHtml + "<div class='row zfBox' id='tabs'>";
            appendHtml = appendHtml + "<span>";
            appendHtml = appendHtml + "<ul class='col-md-12 col-sm-12'>";
            appendHtml = appendHtml + "<li class='col-md-6 col-sm-6 leftLine' id='payType' onclick='openPayTab()'>支付类型</li>";
            appendHtml = appendHtml + "<li class='col-md-6 col-sm-6 ' id='mchType' onclick='openMchTab()'>渠道信息</li>";
            appendHtml = appendHtml + "</ul>";
            appendHtml = appendHtml + "</span>";

            appendPayHtml = appendPayHtml + appendHtml;
            appendPayHtml = appendPayHtml + "<span id='payRate'>";
            appendPayHtml = appendPayHtml + "<div class='col-md-12 col-sm-12'>";
            appendPayHtml = appendPayHtml + "<div class='col-md-6 col-sm-6'>" + data.dt_name + "</div>";
            appendPayHtml = appendPayHtml + "<div class='col-md-4 col-sm-4'>费率</div>";
            appendPayHtml = appendPayHtml + "<div class='col-md-2 col-sm-2'>状态</div>";
            appendPayHtml = appendPayHtml + "</div>";
            appendPayHtml = appendPayHtml + "<span>";
            appendPayHtml = appendPayHtml + payHtml;
            appendPayHtml = appendPayHtml + "</span>";
            appendPayHtml = appendPayHtml + "</span>";
            appendPayHtml = appendPayHtml + "</div>";
            appendPayHtml = appendPayHtml + modifyHtml;
            data.auth_info.sort(valueSort('desc', 'auth_at'));
            for (var auth_index = 0; auth_index < data.auth_info.length; auth_index++) {
                if (data.auth_info[auth_index].auth_status == 3 || data.auth_info[auth_index].auth_status == 7) {
                    var target_index = 'auth_' + auth_index;
                    authHtml = authHtml + "<div><span>" + data.auth_info[auth_index].auth_at + "<a data-toggle='modal' data-target=" + "#" + target_index + ">" + data.auth_info[auth_index].comment + "</a>" + " " + data.auth_info[auth_index].auth_user + "</span></div>";

                    //查看驳回原因弹框
                    authHtml = authHtml + '<div class="modal fade" id=' + target_index + ' tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">'
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
            data.activated_info.sort(valueSort('desc','activated_at'));
            for(var i=0;i<data.activated_info.length;i++){
                for( _key in AVAILABLE_PAYMENTS){
                    if(data.activated_info[i].uline_payment_code == _key){
                        activateHtml = activateHtml + "<div><span>" + data.activated_info[i].activated_at + " " + AVAILABLE_PAYMENTS[_key] + " " + data.activated_info[i].comment + "</span></div>";
                    }
                }
            }


            appendMchInfoHtml = appendHtml + "<span id='mchInfo'>";
            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>基本信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>渠道编号</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.dt_id;
            if (data.rate == 1){
                appendMchInfoHtml = appendMchInfoHtml + "(0费率)";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</span>"
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
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
            appendMchInfoHtml = appendMchInfoHtml + "<h4>联系信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系人</label><span>" + data.contact + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系电话</label><span>" + data.mobile + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>电子邮箱</label><span>" + data.email + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>经营信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>ULINE行业</label><span>"+ data.u_ind_name +"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>微信渠道号(2‰)</label><span>"+ data.wx_channel_id +"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>微信渠道号(6‰)</label><span>"+ data.wx_app_channel_id +"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>微信经营类目</label><span>"+ data.wx_ind_name +"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>微信经营类目id</label><span>"+ data.wx_ind_code +"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>支付宝行业</label><span>"+ data.ali_ind_name +"</span></div>";
            if (data.service_phone == null) {
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>客服电话</label><span>" + data.mobile + "</span></div>";
            } else {
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>客服电话</label><span>" + data.service_phone + "</span></div>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";

            // 如果出现其他值， 尽量显示成普通渠道商
            if (data.dt_type == "2") {
                DtTypeDisplay = '银行内部渠道商'
            } else {
                DtTypeDisplay = '普通渠道商'

            }
            appendMchInfoHtml = appendMchInfoHtml + "<h4>渠道基本信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>渠道类型</label><span>" + DtTypeDisplay + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>渠道名称</label><span>" + data.dt_name + "</span></div>";
            if(data.district == null){
                data.district='';
            }
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>省份城市</label><span>"+ data.province + data.city +  data.district + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系地址</label><span>" + data.address +"</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>渠道负责人信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>身份证</label><span>" + data.id_card_no + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>身份证照片</label><span>";
            appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.id_card_img_f + "' target='_blank'><img src='" + data.id_card_img_f + "'/></a>";
            appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.id_card_img_b + "' target='_blank'><img src='" + data.id_card_img_b + "'/></a>";
            appendMchInfoHtml = appendMchInfoHtml + "</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>营业执照信息</h4>";
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
                if (data.license_period) {
                    if (data.license_end_date) {
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
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>营业执照照片</label><span>";
                appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.license_img + "' target='_blank'><img src='" + data.license_img + "'/></a>";
                appendMchInfoHtml = appendMchInfoHtml + "</span></div>"
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>结算信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算账号类型</label><span>" + bt_name + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算户名</label><span>" + data.balance_name + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算银行</label><span>" + data.bank_name + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算帐号</label><span>" + data.balance_account + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list_lost'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>操作记录</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + authHtml;
            appendMchInfoHtml = appendMchInfoHtml + activateHtml;
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + modifyHtml;

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
    if (document.getElementById("payType") && document.getElementById("mchType")){
        tableBox.html(appendMchInfoHtml);
    }
    $('#mchType').addClass('leftLine').siblings().removeClass('leftLine');
}
openPayTab();
openMchTab();
