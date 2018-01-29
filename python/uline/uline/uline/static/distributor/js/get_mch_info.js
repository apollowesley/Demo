/**
 * Created by xiezhigang on 16/10/17.
 */
tableBox = $("#mchPayInfo");
appendPayHtml = "";
appendMchInfoHtml = "";
appendAddressHtml = "";
function openNewTable(value) {
    if ($("#tr_"+value).attr('class') == "hover") {
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
        url: '/dist/inlet/mch/detail',
        complete:function(){
            getWxPayConfig(value,true);
        }
    }).done(function(res){
        loadingHide();
        if (res.code == '200') {
            var data = res.data;
            window.mch_id = data.mch_id;
            var imgCardFrontOld = data.id_card_img_f;
            var imgCardBackOld = data.id_card_img_b;
            var img_with_id_cardOld = data.img_with_id_card;
            var appendHtml = "";
            var payHtml = "";
            var authHtml = "";
            var modifyHtml = "";
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
            var checkItem101 = "";
            var checkItem102 = "";
            var checkItem103 = "";
            var checkItem104 = "";
            var checkItem105 = "";
            var checkItem107 = "";
            var checkItem108 = "";
            var checkItem109 = "";
            var toUrl = "";
            var authMchStatusHtml = "";
            var bt_name = "";

            var licenseNum = "";
            var licenseStartDate = "";
            var licenseEndDate = "";
            var licensePeriod = "";
            var licenseScope = "";
            var paymentStr = "";
            var aliRole=1;
            var wxRole=1;

            if (data.balance_type == 1) {
                bt_name = '企业';
            } else if (data.balance_type == 2) {
                bt_name = '个人';
            }

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

            var payUrl='';
            for(var i=0;i<data.payment.length;i++){
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

            var u_ind_name = data.u_ind_name.split('-');

            if (data.auth_status == 2 || data.auth_status == 3 || data.auth_status == 7 ) {
                toUrl = '/dist/inlet/mch/modify?mch_id=' + data.mch_id + '&imgCardFrontOld=' + imgCardFrontOld
                    + '&imgCardBackOld=' + imgCardBackOld
                    + '&industry_no=' + data.u_ind_code + '&email=' + data.email
                    + '&province=' + data.province + '&city=' + data.city + '&contact=' + data.contact + '&mobile=' + data.mobile
                    + '&service_phone=' + data.service_phone + '&balance_type=' + data.balance_type
                    + '&bank_no=' + data.bank_no
                    + '&balance_account=' + data.balance_account + '&industry_name=' + data.industry_name
                    + '&area=' + u_ind_name[0] + '&cmbProvince=' + u_ind_name[1] + '&cmbCity=' + u_ind_name[2] + '&cmbArea=' + u_ind_name[3]
                    +payUrl;

                for(var count=1; count<6; count++){
                    if(data['annex_img' + count]){
                        toUrl += '&annex_img' + count + '=' + data['annex_img' + count];
                    }
                }

                for(var count=1; count<6; count++){
                    if(data['wx_dine_annex_img' + count]){
                        toUrl += '&wx_dine_annex_img' + count + '=' + data['wx_dine_annex_img' + count];
                    }
                }

                if (data.use_dine == 1) {
                    toUrl += '&use_dine=' + data.use_dine;
                }
                // +'&licenseNum='+data.license_num
                // +'&licenseStartDate='+data.license_start_date
                // +'&licenseEndDate='+data.license_end_date
                // +'&licensePeriod='+data.license_period
                // +'&licenseScope='+data.license_scope
                // +'&licenseImgOld='+licenseImgOld;
                //+'&address='+data.address
                //+'&id_card_no='+data.id_card_no
                //+'&bank_name='+data.bank_name
                for(roleKey in data.role){
                    toUrl+='&'+roleKey+'='+data.role[roleKey];
                }
                if (data.license_num) {
                    toUrl += '&license_num=' + data.license_num;
                }
                if (data.license_start_date) {
                    toUrl += '&license_start_date=' + data.license_start_date;
                }
                if (data.license_end_date) {
                    toUrl += '&license_end_date=' + data.license_end_date;
                }
                if (data.license_period) {
                    toUrl += '&license_period=' + data.license_period;
                }
                /*if (data.license_scope){
                 toUrl += '&license_scope='+data.license_scope;
                 }*/
                if (data.dt_sub_id) {
                    toUrl += '&dt_sub_id=' + data.dt_sub_id;
                }
                if (data.dt_sub_name) {
                    toUrl += '&dt_sub_name=' + data.dt_sub_name;
                }
                if(data.district != null){
                    toUrl += '&district=' + data.district;
                }
                if (data.mch_desk_img) {
                    toUrl += '&mch_desk_img=' + data.mch_desk_img;
                }
                if (data.mch_front_img) {
                    toUrl += '&mch_front_img=' + data.mch_front_img;
                }
                if (data.mch_inner_img) {
                    toUrl += '&mch_inner_img=' + data.mch_inner_img;
                }

                if(data.img_with_id_card ){
                    toUrl += '&img_with_id_cardOld=' + img_with_id_cardOld;
                }
                if(data.head_name ){
                    toUrl += '&head_name=' + data.head_name;
                }
                if(data.head_mobile ){
                    toUrl += '&head_mobile=' + data.head_mobile;
                }
                if(data.license_type ){
                    toUrl += '&license_type=' + data.license_type;
                }
                if(data.head_type ){
                    toUrl += '&head_type=' + data.head_type;
                }
                toUrl += '&licenseImgOld='+data.license_img;
                modifyHtml = modifyHtml + "<a class='btn btn-default btnTop' onclick=setRateCookie('"+paymentStr+"') href='"+toUrl+"'>修改</a>";
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
            if(data.subsidize_info){
                if(data.subsidize_info.weixin != null ){
                    payHtml+='<div class="role-box col-md-12">微信支付手续费补贴： '+data.subsidize_info.weixin+'%</div>';
                }
                if(data.subsidize_info.alipay != null ){
                    payHtml+='<div class="role-box col-md-12">支 付 宝 手续费补贴： '+data.subsidize_info.alipay+'%</div>';
                }
            }
            /*-------------------信用卡操作-----------------------*/
            if(data.credit_status) {
                if (data.credit_status.weixin != 1) {
                    payHtml += '<div class="role-box col-md-12">' +
                        '<span class="m-right-5">微信支付信用卡支付权限：正常</span>' +
                        '</div>';
                } else {
                    payHtml += '<div class="role-box col-md-12">' +
                        '<span class="m-right-5">微信支付信用卡支付权限：已关闭</span>' +
                        '</div>';
                }
                if (data.credit_status.alipay != 1) {
                    payHtml += '<div class="role-box col-md-12">' +
                        '<span class="m-right-5">支 付 宝 信用卡支付权限：正常</span>' +
                        '</div>';
                } else {
                    payHtml += '<div class="role-box col-md-12">' +
                        '<span class="m-right-5">支 付 宝 信用卡支付权限：已关闭</span>' +
                        '</div>';
                }
            }
            if(data.unionpay_limit){
                payHtml+='<div class="role-box col-md-12">银联限额： '+data.unionpay_limit+'</div>';
            }

            appendHtml = appendHtml + "<div class='row zfBox' id='tabs'>";
            appendHtml = appendHtml + "<span>";
            appendHtml = appendHtml + "<ul class='col-md-12 col-sm-12 table-choose'>";
            appendHtml = appendHtml + "<li class='col-md-4 col-sm-4 leftLine' id='payType'>支付类型</li>";
            appendHtml = appendHtml + "<li class='col-md-4 col-sm-4 ' id='mchType'>商户信息</li>";
            appendHtml = appendHtml + "<li class='col-md-4 col-sm-4 ' id='addType' >商户配置</li>";
            appendHtml = appendHtml + "</ul>";
            appendHtml = appendHtml + "</span>";

            appendPayHtml = appendPayHtml + appendHtml;
            appendPayHtml = appendPayHtml + "<span id='payRate'>";
            appendPayHtml = appendPayHtml + "<div class='col-md-12 col-sm-12'>";
            appendPayHtml = appendPayHtml + "<div class='col-md-6 col-sm-6'>" + data.mch_name + "</div>";
            appendPayHtml = appendPayHtml + "<div class='col-md-4 col-sm-4'>费率</div>";
            appendPayHtml = appendPayHtml + "<div class='col-md-2 col-sm-2'>状态</div>";
            appendPayHtml = appendPayHtml + "</div>";
            appendPayHtml = appendPayHtml + "<span>";
            appendPayHtml = appendPayHtml + payHtml;
            appendPayHtml = appendPayHtml + "</span>";
            appendPayHtml = appendPayHtml + "</span>";
            appendPayHtml = appendPayHtml + "</div>";
            appendPayHtml = appendPayHtml + modifyHtml;

            var callback = '未设置';
            if (data.pay_notify_url != "" && data.pay_notify_url != null) {
                callback = data.pay_notify_url;
            }
            ;

            appendAddressHtml = appendAddressHtml + appendHtml;
            appendAddressHtml = appendAddressHtml + "<div id='add-callback'>";
            appendAddressHtml = appendAddressHtml + "<p>固定收款二维码回调地址</p>";
            appendAddressHtml = appendAddressHtml + "<div><span class='add-callback' id=" + "add-callback-" + value + ">" + callback + "</span><a data-toggle='modal' data-target=" + "#addressModal-" + value + ">修改</a></div>";
            appendAddressHtml = appendAddressHtml + "<div>针对商户需要使用ULINE生成的商户固定支付二维码,且需要交易回调时,在此填写需要回调的URL<br>若无此需求,不需要填写</div>";
            appendAddressHtml = appendAddressHtml + "</div>";

            appendAddressHtml = appendAddressHtml + "<div id='add-callback'>";
            appendAddressHtml = appendAddressHtml + "<p>开户邮件接收方</p>";
            appendAddressHtml = appendAddressHtml + "<div><span class='m-right-5'>" + data.activate_email_tag + "</span>";
            if(data.activated_status==2){
                appendAddressHtml = appendAddressHtml + "<a href='javascript:;' id='resend-email' onclick='resendActiveEmail("+value+");'>重新发送激活邮件</a></div>";
            }
            appendAddressHtml = appendAddressHtml + "</div>";

            /*-----------------------------------------------微信支付配置 start-----------------------------------------------------------*/

            appendAddressHtml += "<div class='wx-config-wrap'></div>";
            $('#thisMchId').val(value);

            /*-----------------------------------------------微信支付配置 end-----------------------------------------------------------*/

            appendAddressHtml = appendAddressHtml + '<div class="modal fade addressBox" id='+ "addressModal-"+ value + ' tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">'
            appendAddressHtml = appendAddressHtml + '<div class="modal-dialog">'
            appendAddressHtml = appendAddressHtml + '<div class="modal-content">'
            appendAddressHtml = appendAddressHtml + '<div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h4 class="modal-title" id="myModalLabel">固定收款二维码回调地址</h4></div>'
            appendAddressHtml = appendAddressHtml + '<div class="modal-body">'
            appendAddressHtml = appendAddressHtml + '<form method="post"><input type="text" id=' + "input—" + value + ' maxlength="200"/></form>';
            appendAddressHtml = appendAddressHtml + '<div>例: http://pay.uboss.cn</div>';
            appendAddressHtml = appendAddressHtml + '</div>';
            appendAddressHtml = appendAddressHtml + '<div class="modal-footer"><button class="btn btn-primary" data-dismiss="modal" id="address-conf" onclick="postMerchant('+value+')">确认</button></div>';
            appendAddressHtml = appendAddressHtml + '</div>';
            appendAddressHtml = appendAddressHtml + '</div>';
            appendAddressHtml = appendAddressHtml + '</div>';
            appendAddressHtml = appendAddressHtml + '</div>';
            appendAddressHtml = appendAddressHtml + modifyHtml;

            data.auth_info.sort(valueSort('desc', 'auth_at'));
            for (var auth_index=0; auth_index < data.auth_info.length; auth_index++){
                if (data.auth_info[auth_index].auth_status == 3 || data.auth_info[auth_index].auth_status == 7 ) {
                    var target_index=  'auth_' + auth_index;
                    authHtml = authHtml + "<div><span>" + data.auth_info[auth_index].auth_at + "<a data-toggle='modal' data-target=" + "#" + target_index  +  ">" + data.auth_info[auth_index].comment + "</a></span></div>";

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
                    authHtml = authHtml + "<div><span>" + data.auth_info[auth_index].auth_at + " " + data.auth_info[auth_index].comment + "</span></div>";
                }
            }
            data.activated_info.sort(valueSort('desc','activated_at'));
            for(var i=0;i<data.activated_info.length;i++){
                for( _key in AVAILABLE_PAYMENTS){
                    if(data.activated_info[i].uline_payment_code == _key){
                        activateHtml = activateHtml + "<div><span>"+ data.activated_info[i].activated_at+ " " + AVAILABLE_PAYMENTS[_key]+ " " +data.activated_info[i].comment+"</span></div>";
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
                authMchStatusHtml = authMchStatusHtml + "<span>" + data.mch_id + qrCodeHtml +"</span>";
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
                    if(data.use_dine && data.use_dine == 1){
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
            appendMchInfoHtml = appendMchInfoHtml + "<h4>基本信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + authMchStatusHtml;
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>业务员</label><span>" + data.dt_sub_user +"</span></div>";
            if(res.INTER_BANK){
                if(data.bk_type == 1){
                    appendMchInfoHtml = appendMchInfoHtml + "<div><label>所属银行</label><span>主银行</span></div>";
                }else if(data.bk_type == 2){
                    appendMchInfoHtml = appendMchInfoHtml + "<div><label>所属银行</label><span>" + data.bk_name + "</span></div>";
                }
            }
            if(data.ali_sub_mch_id ){
                if(data.ali_level==null){data.ali_level='--'}
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>支付宝商户号(线下)</label><span>" + data.ali_sub_mch_id + "</span></div>";
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>支付宝商户分级</label><span><em>" + data.ali_level + "</em><a href='javascript:;' onclick='updateAliLevel("+value+",$(this))'> 更新</a></span></div>";
            }
            if(data.jd_sub_mch_id ) {
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>京东商户号</label><span>" + data.jd_sub_mch_id + "</span></div>";
            }
            if(data.unionpay_level && data.unionpay_level != ''){
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>银联商户等级</label><span>"+data.unionpay_level+"</span></div>";
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
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>商户简称</label><span>"+data.mch_shortname+"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>经营类目</label><span>"+ data.u_ind_name +"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>客服电话</label><span>" + data.service_phone + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>商户基本信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>商户名称</label><span>"+data.mch_name+"</span></div>";
            if(data.district == null){
                data.district='';
            }
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>省份城市</label><span>"+ data.province + data.city +  data.district + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系地址</label><span>" + data.address +"</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>商户负责人信息</h4>"
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

            appendMchInfoHtml = appendMchInfoHtml + "<h4>商户执照信息</h4>"
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
                appendMchInfoHtml = appendMchInfoHtml + "<label>营业执照照片</label><span>";
                appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.license_img + "' target='_blank'><img src='" + data.license_img + "'/></a>";
                appendMchInfoHtml = appendMchInfoHtml + "</span></div>";
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

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>结算信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算账号类型</label><span>" + bt_name + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算户名</label><span>" + data.balance_name + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算银行</label><span>" + data.bank_name + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>结算帐号</label><span>" + data.balance_account + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list_lost'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>操作记录</h4>"
            appendMchInfoHtml = appendMchInfoHtml + authHtml;
            appendMchInfoHtml = appendMchInfoHtml + activateHtml;
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + modifyHtml;

            if(data.activated_status==1){
                $("#tr_"+value).find('td').eq(3).text('未激活');
            }else if(data.activated_status==2){
                $("#tr_"+value).find('td').eq(3).text('已激活');
            }

            tableBox.append('<div class="table-box">'+appendPayHtml+'</div>');
            tableBox.append('<div class="table-box">'+appendMchInfoHtml+'</div>');
            tableBox.append('<div class="table-box">'+appendAddressHtml+'</div>');
            $('.table-box').eq(0).show();

                        //调用函数
            // getAddress();
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
openPayTab();
openMchTab();


function getAddress(value){
    $("#address-conf").click(function(){
        postMerchant();
    })
}

function postMerchant(value) {
    function getCookie(name) {
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    }
    var xsrf = getCookie("_xsrf");
    var $add = "input—" + String(value);
    var $setUp = "add-callback-" + String(value);
    var commentVal = document.getElementById($add).value;
    var setComment = document.getElementById($setUp);
    $.ajax({
        headers: {"X-XSRFToken":xsrf},
        url :'/dist/inlet/mch/callbackurl',
        type:'post',
        data: {"pay_notify_url":commentVal,"mch_id": value},
        success:function(data){
            if($(setComment).html() != commentVal){
                $(setComment).html(data.data.pay_notify_url);
            }
        },
        error: function(){
            //请求出错处理
            alert('修改失败,请重试')
        }

    })
}

function getMerchant(value){
    $.ajax({
        url:'/dist/inlet/mch/callbackurl',
        type:'get',
        data: {"pay_notify_url": value},
        success:function(data){
            if(data.code==200){
                 $('#address-callback').html(value);
            }
        },
        error: function(){
            //请求出错处理
            alert('修改失败,请重试')
        }
    })
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
function resendActiveEmail(mch_id){
    var confirmSend = confirm("确定需要重新发送激活邮件？");
    if(!confirmSend){
        return;
    }
    $('body').ulaiberLoading({loadingStatus:true});
    $.ajax({
        type: 'GET',
        data: {"mch_id": mch_id},
        dataType: 'json',
        url: '/dist/inlet/mch/resend_active_email'
    }).done(function(res){
        var code = res.code;
        $('body').ulaiberLoading({loadingStatus:false});
        if(code == 200){
            errorTip('发送成功');
        }else{
            errorTip('发送失败');
        }
    }).fail(function(res){
        $('body').ulaiberLoading({loadingStatus:false});
        errorTip('请求出错，请重试');
    })
}