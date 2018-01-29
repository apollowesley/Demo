/**
 * Created by xiezhigang on 16/10/17.
 */
tableBox = $("#mchPayInfo");
appendPayHtml = "";
appendMchInfoHtml = "";
appendAddressHtml = "";
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
    tableBox.html('');
    loadingShow();
    appendPayHtml = "";
    appendMchInfoHtml = "";
    appendAddressHtml = "";
    $.ajax({
        type: 'GET',
        data: {"mch_id": value},
        dataType: 'json',
        url: '/inter_bank/inlet/mch/detail',
        complete:function(){
            getWxPayConfig(value,false);
        }
    }).done(function (res) {
        loadingHide();
        if (res.code == '200') {
            var data = res.data;
            window.mch_id = data.mch_id;
            var appendHtml = "";
            var payHtml = "";
            var authHtml = "";
            var activateHtml = "";
            var qrCodeHtml = "";

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
            var activatedHtml = "";
            var authMchStatusHtml = "";
            var bt_name = "";
            var activatedHtml = "";
            var activatedBatchHtml = "";
            var paymentTypeArr = [];

            var licenseNum = "";
            var licenseStartDate = "";
            var licenseEndDate = "";
            var licensePeriod = "";
            var licenseScope = "";
            var licenseImgOld = data.license_img;
            var use_dine=0;
            var aliRole=0;
            var wxRole=0;

            if(data.balance_type==1){
                bt_name = '企业';
            }else if(data.balance_type==2){
                bt_name = '个人';
            }

            for (var payIndex = 0; payIndex < data.payment.length; payIndex++) {
                paymentTypeArr[payIndex] = data.payment[payIndex].activated_status;
            }
            if (data.auth_status == 2){
                $("#tr_"+value).children().eq(5).html('审核通过');
            }
            activatedBatchHtml+="<div class='col-md-12 col-sm-12' id='activated_batch'>"

                for (var arrIndex = 0; arrIndex < paymentTypeArr.length; arrIndex++) {
                    if (data.auth_status == 2 && paymentTypeArr[arrIndex] == 1) {
                        activatedBatchHtml = activatedBatchHtml + "<a href='javascript:void(0);' onclick='activatedBatchMchInletStatus(" + data.mch_id + ")'>激活全部</a>";
                        break;
                    }
                }
                for (var arrIndex = 0; arrIndex < paymentTypeArr.length; arrIndex++) {
                    if (paymentTypeArr[arrIndex] == 2) {
                        var url = '/inter_bank/inlet/mch/batchClose';
                        activatedBatchHtml = activatedBatchHtml + "<a style='margin-left:15px;' href='javascript:void(0);' onclick=rateCloseAll('" + url + "'," + data.mch_id + ")>关闭全部</a>";
                        break;
                    }
                }

            activatedBatchHtml+="</div>";

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
            var status_index=0;
            for(var i=0;i<data.payment.length;i++){
                for( _key in AVAILABLE_PAYMENTS){
                    if(data.payment[i].uline_payment_code == _key){
                        payHtml+='<div class="col-md-5 col-sm-5" style="text-align:left;padding-left:10px;">'+AVAILABLE_PAYMENTS[_key]+'</div><div class="col-md-3 col-sm-3">'+data.payment[i].pay_rate+'‰ </div>';
                        if (data.auth_status==2 && (data.payment[i].activated_status == 1 || data.payment[i].activated_status==3)) {
                            activatedName = '未激活';
                            if(data.payment[i].operate==1) {
                                activatedHtml = "<a href='javascript:;' id=" + "td_" + data.payment[i].uline_payment_code + " onclick=activatedMchInletStatus(" + data.mch_id + ",'" + data.payment[i].uline_payment_code + "')>激活</a >"
                            }else{
                                activatedHtml = '';
                            }
                        }else if(data.payment[i].activated_status==2){
                            status_index++;
                            activatedName = '激活状态';
                            var data_url='/inter_bank/inlet/mch/close';
                            activatedHtml = "<a href='javascript:;' onclick=rateClose('" + data_url + "'," + data.mch_id + ",'" + data.payment[i].uline_payment_code + "','" + payTypeName + "')>关闭</a >"
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
                if(data.payment[i].uline_payment_code.indexOf('WX_DINE')>=0){
                    use_dine=1;
                }
            }

            if(status_index == 0){
                $("#tr_"+value).children().eq(4).html('未激活');
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
            /*-------------------风控操作-----------------------*/
            if(data.balance_status != 1 ){
                roleHtml += '<div class="role-box col-md-12">' +
                            '<span class="m-right-5">结算账户状态：正常</span>' +
                            '<a href="javascript:;" class="m-left-5" _params={"role_id":"'+value+'","role_type":"mch","platform":"1","action":"close"} data-click="settleOperate">冻结</a> ' +
                            '</div>';
            }else{
                roleHtml += '<div class="role-box col-md-12">' +
                            '<span class="m-right-5">结算账户状态：系统冻结</span>' +
                            '<a href="javascript:;" class="m-left-5" _params={"role_id":"'+value+'","role_type":"mch","platform":"","action":"open"} data-click="settleOperate">恢复</a> ' +
                            '</div>';
            }
            /*-------------------信用卡操作-----------------------*/
            if(data.credit_status) {
                if (data.credit_status.weixin != 1) {
                    roleHtml += '<div class="role-box col-md-12">' +
                        '<span class="m-right-5">微信支付信用卡支付权限：正常</span>' +
                        '<a href="javascript:;" class="m-left-5" _params={"role_id":"' + value + '","role_type":"mch","platform":"weixin","action":"close"} data-click="creditOperate">关闭</a> ' +
                        '</div>';
                } else {
                    roleHtml += '<div class="role-box col-md-12">' +
                        '<span class="m-right-5">微信支付信用卡支付权限：已关闭</span>' +
                        '<a href="javascript:;" class="m-left-5" _params={"role_id":"' + value + '","role_type":"mch","platform":"weixin","action":"open"} data-click="creditOperate">开启</a> ' +
                        '</div>';
                }
                if (data.credit_status.alipay != 1) {
                    roleHtml += '<div class="role-box col-md-12">' +
                        '<span class="m-right-5">支 付 宝 信用卡支付权限：正常</span>' +
                        '<a href="javascript:;" class="m-left-5" _params={"role_id":"' + value + '","role_type":"mch","platform":"alipay","action":"close"} data-click="creditOperate">关闭</a> ' +
                        '</div>';
                } else {
                    roleHtml += '<div class="role-box col-md-12">' +
                        '<span class="m-right-5">支 付 宝 信用卡支付权限：已关闭</span>' +
                        '<a href="javascript:;" class="m-left-5" _params={"role_id":"' + value + '","role_type":"mch","platform":"alipay","action":"open"} data-click="creditOperate">开启</a> ' +
                        '</div>';
                }
            }
            if(data.unionpay_limit){
                roleHtml+='<div class="role-box col-md-12">银联限额： '+data.unionpay_limit+'</div>';
            }

            appendHtml = appendHtml + "<div class='row zfBox' id='tabs'>";
            appendHtml = appendHtml + "<span>";
            appendHtml = appendHtml + "<ul class='col-md-12 col-sm-12 table-choose'>";
            appendHtml = appendHtml + "<li class='col-md-4 col-sm-4 leftLine' id='payType'>支付类型</li>";
            appendHtml = appendHtml + "<li class='col-md-4 col-sm-4 ' id='mchType'>商户信息</li>";
            appendHtml = appendHtml + "<li class='col-md-4 col-sm-4 ' id='addType'>商户配置</li>";
            appendHtml = appendHtml + "</ul>";
            appendHtml = appendHtml + "</span>";

            appendPayHtml = appendPayHtml + appendHtml;
            appendPayHtml = appendPayHtml + "<span id='payRate'>";
            appendPayHtml = appendPayHtml + "<div class='col-md-12 col-sm-12'>";
            if(data.risk_info.risk_msg != '' && data.risk_info.risk_msg != undefined){
                appendPayHtml = appendPayHtml + "<div style='padding:15px 5px 10px 5px;margin:0 10px;border-bottom:1px solid #ccc;color:#ff671a;'>"+ data.risk_info.risk_msg +"</div>";
            }
            appendPayHtml = appendPayHtml + "<div class='col-md-6 col-sm-6'>" + data.mch_name + "</div>";
            appendPayHtml = appendPayHtml + "<div class='col-md-2 col-sm-2'>费率</div>";
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


            var callback = '未设置';
            if( data.pay_notify_url != "" && data.pay_notify_url != null){
                callback = data.pay_notify_url;
            };

            appendAddressHtml = appendAddressHtml + appendHtml;
            appendAddressHtml = appendAddressHtml + "<div id='add-callback'>";
            appendAddressHtml = appendAddressHtml + "<p>固定收款二维码回调地址</p>";
            appendAddressHtml = appendAddressHtml + "<div><span>"+callback+"</span></div>";
            appendAddressHtml = appendAddressHtml + "</div>";
                appendAddressHtml = appendAddressHtml + "<div id='add-callback'>";
                appendAddressHtml = appendAddressHtml + "<p>开户邮件接收方</p>";
                appendAddressHtml = appendAddressHtml + "<div><span class='m-right-5'>" + data.activate_email_tag + "</span></div>";
                appendAddressHtml = appendAddressHtml + "</div>";

            /*-----------------------------------------------微信支付配置 start-----------------------------------------------------------*/

            appendAddressHtml += "<div class='wx-config-wrap'></div>";
            $('#thisMchId').val(value);

            /*-----------------------------------------------微信支付配置 end-----------------------------------------------------------*/

            data.auth_info.sort(valueSort('desc', 'auth_at'));
            for (var auth_index = 0; auth_index < data.auth_info.length; auth_index++) {
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
                }else if(data.auth_info[auth_index].auth_status == 6){
                    var auth_comment=data.auth_info[auth_index].auth_comment;
                    auth_comment=auth_comment.replace(' ', ',');
                    authHtml = authHtml +"<div><span>"+data.auth_info[auth_index].auth_at+"</span><span class='inleting-tip base-error-c cursor' onclick=errorTipBtn('"+auth_comment+"')> "+data.auth_info[auth_index].comment+" </span><span> "+data.auth_info[auth_index].auth_user+"</span></div>"
                } else {
                    authHtml = authHtml + "<div><span>" + data.auth_info[auth_index].auth_at + " " + data.auth_info[auth_index].comment + " " + data.auth_info[auth_index].auth_user + "</span></div>";
                }
            }

            data.activated_info.sort(valueSort('desc','activated_at'));
            for(var i=0;i<data.activated_info.length;i++){
                for( _key in AVAILABLE_PAYMENTS){
                    if(data.activated_info[i].uline_payment_code == _key){
                        activateHtml = activateHtml + "<div><span>" + data.activated_info[i].activated_at + " " + AVAILABLE_PAYMENTS[_key] + " " + data.activated_info[i].comment + " " + data.activated_info[i].activated_user + "</span></div>";
                    }
                }
            }

            var download_qr_url_small = '/common/qrdownload?text=' + QR_SCAN_URL + '/r?m=' + data.mch_id + '&size=142&save_name=' + data.mch_shortname + '(' +  data.mch_id + ')' + '.jpg';
            var download_qr_url = '/common/qrdownload?text=' + QR_SCAN_URL + '/r?m=' + data.mch_id + '&size=258&save_name=' + data.mch_shortname + '(' +  data.mch_id + ')' + '.jpg';
            var download_qr_url_big = '/common/qrdownload?text=' + QR_SCAN_URL + '/r?m=' + data.mch_id + '&size=430&save_name=' + data.mch_shortname + '(' +  data.mch_id + ')' + '.jpg';

            qrCodeHtml = qrCodeHtml + "<span>";
            qrCodeHtml = qrCodeHtml + "<div class='modal fade' id='qrCode' tabindex='-1' role='dialog' aria-labelledby='myModalLabel' aria-hidden='true'>";
            qrCodeHtml = qrCodeHtml + "<div class='modal-dialog'>";
            qrCodeHtml = qrCodeHtml + "<div class='modal-content'>";
            qrCodeHtml = qrCodeHtml + "<div class='modal-header'>";
            qrCodeHtml = qrCodeHtml + "<button type='button' class='close' data-dismiss='modal' aria-hidden='true'>&times;</button> <h3 class='modal-title'>商户固定收款码</h3>";
            qrCodeHtml = qrCodeHtml + "</div>";
            qrCodeHtml = qrCodeHtml + "<div class='modal-body'><div id='mch_qrCode'></div>" +
                "<p class='qrcode-btn'><a class='code' href=" + download_qr_url_small + "><i class='fa fa-download m-right-5'></i>5cm*5cm</a></p>" +
                "<p class='qrcode-btn'><a class='code' href=" + download_qr_url + "><i class='fa fa-download m-right-5'></i>8cm*8cm</a></p>" +
                "<p class='qrcode-btn'><a class='code' href=" + download_qr_url_big + "><i class='fa fa-download m-right-5'></i>15cm*15cm</a></p>" +
                "</div>";
            qrCodeHtml = qrCodeHtml + "<div class='modal-footer center-block'></div>";
            qrCodeHtml = qrCodeHtml + "</div>";
            qrCodeHtml = qrCodeHtml + "</div>";
            qrCodeHtml = qrCodeHtml + "</div>";
            qrCodeHtml = qrCodeHtml + "<a href='#' data-toggle='modal' data-target='#qrCode' class='ewm' onclick='qrCodePreview("+mch_id+")'><span style='margin-left: 18px;'>二维码</span></a>";
            qrCodeHtml = qrCodeHtml + "</span>";

            if (data.status == 2) {
                authMchStatusHtml = authMchStatusHtml + "<div>";
                authMchStatusHtml = authMchStatusHtml + "<label>商户编号</label>";
                authMchStatusHtml = authMchStatusHtml + "<span>" + data.mch_id + qrCodeHtml + "</span>";
                authMchStatusHtml = authMchStatusHtml + "</div>";
                authMchStatusHtml = authMchStatusHtml + "<div>";
                // authMchStatusHtml = authMchStatusHtml + "<label>微信商户编号:</label>";
                //微信商户编号为空时
                authMchStatusHtml = authMchStatusHtml + "<label>微信商户编号";
                if (data.rate == 1) {
                    authMchStatusHtml = authMchStatusHtml + "(0费率)";
                }
                authMchStatusHtml = authMchStatusHtml + "</label>";
                if(data.wx_sub_mch_id != null) {
                    authMchStatusHtml = authMchStatusHtml + "<span>线下：" + data.wx_sub_mch_id;
                    if(use_dine == 1 ){
                        authMchStatusHtml = authMchStatusHtml + "(围餐)";
                    } else if (data.wx_use_parent == 2) {
                        authMchStatusHtml = authMchStatusHtml + "(渠道商)";
                    }
                    authMchStatusHtml = authMchStatusHtml + "</span>";
                }
                if(data.wx_app_sub_mch_id != null){
                    authMchStatusHtml = authMchStatusHtml + "<span>线上：" + data.wx_app_sub_mch_id + "</span>";
                }
                if(data.wx_sub_mch_id == null && data.wx_app_sub_mch_id == null){
                    authMchStatusHtml = authMchStatusHtml + "<span>无</span>";
                }
                authMchStatusHtml = authMchStatusHtml + "</div>";
            }

            appendMchInfoHtml = appendHtml + "<span id='mchInfo'>";
            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>基本信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + authMchStatusHtml;
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>所属渠道商</label><span>" + data.dt_name + "</span></div>";
            if (data.dt_type == 2 && data.dt_sub_name != null){
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>业务员</label><span>" + data.dt_sub_name + "</span></div>";
            }
            if(data.ali_sub_mch_id ){
                if(data.ali_level==null){data.ali_level='--'}
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>支付宝商户号(线下)</label><span>" + data.ali_sub_mch_id + "</span></div>";
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>支付宝商户分级</label><span><em>" + data.ali_level + "</em><a href='javascript:;' onclick='updateAliLevel("+value+",$(this))'> 更新</a></span></div>";
            }
            if(data.jd_sub_mch_id ){
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>京东商户号</label><span>" + data.jd_sub_mch_id + "</span></div>";
            }

            if(data.unionpay_level && data.unionpay_level != ''){
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>银联商户等级</label><span>"+data.unionpay_level+"</span></div>";
            }

            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>联系信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系人</label><span>" + data.contact + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>手机号码</label><span>" + data.mobile + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>电子邮箱</label><span>" + data.email + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>经营信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>商户简称</label><span>"+ data.mch_shortname+"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>经营类目</label><span>"+ data.u_ind_name +"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>客服电话</label><span>"+ data.service_phone+"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>结算信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算账号类型</label><span>" + bt_name + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算户名</label><span>" + data.balance_name + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算银行</label><span>" + data.bank_name + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算帐号</label><span>" + data.balance_account + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>商户基本信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>商户名称</label><span>" + data.mch_name + "</span></div>";
            if(data.district == null){
                data.district='';
            }
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>省份城市</label><span>"+ data.province + data.city +  data.district + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系地址</label><span>" + data.address + "</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>商户基本信息</h4>"
            if(data.head_type && data.head_type !=''){
                var head_type={
                    'LEGAL_PERSON':'法人',
                    'CONTROLLER':'实际控制人',
                    'AGENT':'代理人',
                    'OTHER':'其他',
                };
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>负责人类型</label><span>" + head_type[data.head_type] + "</span></div>";
            }
            if(data.head_name && data.head_name !=''){
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>负责人姓名</label><span>" + data.head_name + "</span></div>";
            }
            if(data.head_mobile && data.head_mobile !=''){
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>负责人电话</label><span>" + data.head_mobile + "</span></div>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>身份证号码</label><span>" + data.id_card_no + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>身份证照片</label><span>";
            appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.id_card_img_f + "' target='_blank'><img src='" + data.id_card_img_f + "'/></a>";
            appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.id_card_img_b + "' target='_blank'><img src='" + data.id_card_img_b + "'/></a>";
            if(data.img_with_id_card && data.img_with_id_card != '' ){
                appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.img_with_id_card + "' target='_blank'><img src='" + data.img_with_id_card + "'/></a>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>商户负责人信息</h4>"
            if(data.license_type && data.license_type !=''){
                if(data.license_type == 'NATIONAL_LEGAL'){
                    var license_type='营业执照';
                }else if(data.license_type == 'NATIONAL_LEGAL_MERGE'){
                    var license_type='营业执照（多证合一)';
                }if(data.license_type == 'INST_RGST_CTF'){
                    var license_type='事业单位法人证书';
                }
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>商户证件类型</label><span>" + license_type + "</span></div>";
            }
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
                appendMchInfoHtml = appendMchInfoHtml + "<span><a href='" + data.license_img + "' target='_blank'><img  src='" + data.license_img + "'/></a><span>";
                appendMchInfoHtml = appendMchInfoHtml + "</div>";
            }

            hasAnnexImg = 0;
            for(var imgCount=1; imgCount<6; imgCount++){
                if(data['annex_img' + imgCount]){
                    hasAnnexImg++;
                    if(hasAnnexImg == 1){
                        appendMchInfoHtml = appendMchInfoHtml + "<div>";
                        appendMchInfoHtml = appendMchInfoHtml + "<label>补充材料</label><span>";
                    }
                    appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data['annex_img' + imgCount] + "' target='_blank'><img src='" + data['annex_img' + imgCount] + "'/></a>";
                }
                if(imgCount == 5 && hasAnnexImg > 0){
                    appendMchInfoHtml = appendMchInfoHtml + "</span></div>";
                }
            }
            for (var ii=0; ii < data.payment.length; ii++) {
                if (data.payment[ii].uline_payment_code.indexOf("WX_DINE")>=0) {
                   if (data.mch_desk_img) {
                        appendMchInfoHtml = appendMchInfoHtml + "<h4>围餐上传资料</h4>";
                        appendMchInfoHtml = appendMchInfoHtml + "<div><label>门店照片</label><span>";
                        appendMchInfoHtml = appendMchInfoHtml + "<a class='float-left' href='" + data.mch_desk_img + "' target='_blank'><img src='" + data.mch_desk_img + "'/></a>";
                        appendMchInfoHtml = appendMchInfoHtml + "<a class='float-left' href='" + data.mch_front_img + "' target='_blank'><img src='" + data.mch_front_img + "'/></a>";
                        appendMchInfoHtml = appendMchInfoHtml + "<a class='float-left' href='" + data.mch_inner_img + "' target='_blank'><img src='" + data.mch_inner_img + "'/></a>";
                        appendMchInfoHtml = appendMchInfoHtml + "</span></div>"
                    }
                    hasWxAnnexImg = 0;
                    for (var imgCount = 1; imgCount < 6; imgCount++) {
                        if (data['wx_dine_annex_img' + imgCount]) {
                            hasWxAnnexImg++;
                            if (hasWxAnnexImg == 1) {
                                appendMchInfoHtml = appendMchInfoHtml + "<div>";
                                appendMchInfoHtml = appendMchInfoHtml + "<label>围餐补充材料</label><span>";
                            }
                            appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data['wx_dine_annex_img' + imgCount] + "' target='_blank'><img src='" + data['wx_dine_annex_img' + imgCount] + "'/></a>";
                        }
                        if (imgCount == 5 && hasWxAnnexImg > 0) {
                            appendMchInfoHtml = appendMchInfoHtml + "</span></div>";
                        }
                    }
                    ii=data.payment.length;
                }
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list_lost'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>操作记录</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + authHtml;
            appendMchInfoHtml = appendMchInfoHtml + activateHtml;
            appendMchInfoHtml = appendMchInfoHtml + "</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            tableBox.append('<div class="table-box">'+appendPayHtml+'</div>');
            tableBox.append('<div class="table-box">'+appendMchInfoHtml+'</div>');
            tableBox.append('<div class="table-box">'+appendAddressHtml+'</div>');
            $('.table-box').eq(0).show();
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
    if (document.getElementById("payType") && document.getElementById("mchType") && document.getElementById("addType")){
        tableBox.html(appendPayHtml);
    }
    $('#payType').addClass('leftLine').siblings().removeClass('leftLine');
}
function openMchTab() {
    if (document.getElementById("payType") && document.getElementById("mchType") && document.getElementById("addType")){
        tableBox.html(appendMchInfoHtml);
    }
    $('#mchType').addClass('leftLine').siblings().removeClass('leftLine');
}
function openAddType() {
    if (document.getElementById("payType") && document.getElementById("mchType") && document.getElementById("addType")){
        tableBox.html(appendAddressHtml);
    }
    $('#addType').addClass('leftLine').siblings().removeClass('leftLine');
}

openPayTab();
openMchTab();
function activatedMchInletStatus(mch_id, pay_type) {
    // 激活支付方式
    $.ajax({
        type: 'GET',
        data: {"mch_id": mch_id, "pay_type": pay_type},
        dataType: 'json',
        url: '/inter_bank/inlet/mch/activated',
        beforeSend: function (XMLHttpRequest) {
            // 请求前处理
        },
        success: function (res) {
            // 请求成功处理
            if (res.code == 200) {
                td = "#td_" + pay_type;
                act = "#act_"  + pay_type;
                $(td).html("");
                $(act).html("已激活");

                tr = "#tr_" + mch_id;
                $(tr + " td:nth-child(5)").html("已激活");
                errorTip('激活成功');
                setTimeout(function(){
                    openNewTable(mch_id,1);
                },2000);
            }else if(res.code==407) {
                errorTipBtn(res.msg)
            }else{
                errorTip('激活失败');
            }
        },
        complete: function (XMLHttpRequest, textStatus) {
            // 完成请求处理
        },
        error: function () {
            // 请求出错处理
            $("#mch_activation").append("<div class='passBox'>操作失败</div>");
            $(".passBox").delay(1000).fadeOut(2000);
        }
    });
    var e = window.event;
    if (e.stopPropagation()) {
        e.stopPropagation();
    } else {
        e.cancelBubble = true;
    }
}


//激活全部
function activatedBatchMchInletStatus(mch_id) {
    // 激活支付方式
    $.ajax({
        type: 'GET',
        data: {"mch_id": mch_id},
        dataType: 'json',
        url: '/inter_bank/inlet/mch/batchActivated',
        beforeSend: function (XMLHttpRequest) {
            // 请求前处理
        },
        success: function (res) {
            // 请求成功处理
            if (res.code == 200) {
                $("[id^=td_]").html("");
                $("[id^=act_]").html("已激活");
                $("#activated_batch").remove();

                tr = "#tr_" + mch_id;
                $(tr + " td:nth-child(5)").html("已激活");
                errorTip('激活成功');
                setTimeout(function(){
                    openNewTable(mch_id,1);
                },2000);
            } else if(res.code==407) {
                errorTipBtn(res.msg);
            }else{
                errorTip('激活失败');
            }
        },
        complete: function (XMLHttpRequest, textStatus) {
            // 完成请求处理
        },
        error: function () {
            // 请求出错处理
            $("#mch_activation").append("<div class='passBox'>操作失败</div>");
            $(".passBox").delay(1000).fadeOut(2000);
        }
    });
    var e = window.event;
    if (e.stopPropagation()) {
        e.stopPropagation();
    } else {
        e.cancelBubble = true;
    }
}

function qrCodePreview(mch_id) {
    var text = QR_SCAN_URL + "/r?m=" + mch_id;
    $("#mch_qrCode").html('');
    $("#mch_qrCode").qrcode({
        render: "canvas",
        width: 200, //宽度
        height: 200, //高度
        color: "#3a3",
        text: text
    });
}

$(document).on('click','.table-choose li',function(e){
    e.stopPropagation();
    e.preventDefault();
    var index=$(this).index();
    console.log($(this).index());
    $('.table-choose li').removeClass('leftLine');
    $('.table-box').eq(index).find('.table-choose li').eq(index).addClass('leftLine');
    $('.table-box').eq(index).show().siblings('.table-box').hide();
});
