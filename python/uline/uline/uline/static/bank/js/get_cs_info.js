/**
 * Created by xiezhigang on 16/10/17.
 */
tableBox = $("#mchPayInfo");
appendPayHtml = "";
appendMchInfoHtml = "";
appendAddressHtml = "";
function openNewTable(value,_status,type) {
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
    appendPayHtml = "";
    appendMchInfoHtml = "";
    appendAddressHtml = "";
    $.ajax({
        type: 'GET',
        data: {"mch_id": value},
        dataType: 'json',
        url: '/bank/inlet/cs/detail'
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

            //
            if(type){
               $('#tr_'+value+' td').eq(2).html(data.parent_short_name+'<a style="text-decoration: none;"> ('+data.mch_shortname+') </a>');
                $('#tr_'+value+' td').eq(1).html(data.parent_name);
            }
            if(data.balance_type==1){
                bt_name = '企业';
            }else if(data.balance_type==2){
                bt_name = '个人';
            }

            for (var payIndex = 0; payIndex < data.payment.length; payIndex++) {
                paymentTypeArr[payIndex] = data.payment[payIndex].activated_status;
            }
            activatedBatchHtml+="<div class='col-md-12 col-sm-12' id='activated_batch'>"
            if(data.bk_id==1) {
                for (var arrIndex = 0; arrIndex < paymentTypeArr.length; arrIndex++) {
                    if (data.auth_status == 2 && paymentTypeArr[arrIndex] == 1) {
                        activatedBatchHtml = activatedBatchHtml + "<a href='javascript:void(0);' onclick='activatedBatchMchInletStatus(" + data.mch_id + ")'>激活全部</a>";
                        break;
                    }
                }
                for (var arrIndex = 0; arrIndex < paymentTypeArr.length; arrIndex++) {
                    if (paymentTypeArr[arrIndex] == 2) {
                        var url = '/bank/inlet/mch/batchClose';
                        activatedBatchHtml = activatedBatchHtml + "<a style='margin-left:15px;' href='javascript:void(0);' onclick=rateCloseAll('" + url + "'," + data.mch_id + ")>关闭全部</a>";
                        break;
                    }
                }
            }
            activatedBatchHtml+="</div>";

            data.payment.sort(valueSort('asc','pay_type'));
            var status_index=0;
            for (var index = 0; index < data.payment.length; index++) {
                if (data.payment[index].pay_type == 1) {
                    payTypeName = '微信－扫码支付';
                    checkItem1 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 2) {
                    payTypeName = '微信－刷卡支付';
                    checkItem2 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 3) {
                    payTypeName = '微信－公众账号支付';
                    checkItem3 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 4) {
                    payTypeName = '微信－APP支付';
                    checkItem4 = data.payment[index].pay_rate;
                }else if(data.payment[index].pay_type==7){
                    payTypeName = '支付宝－扫码支付';
                    checkItem7 = data.payment[index].pay_rate;
                } else if(data.payment[index].pay_type==8){
                    payTypeName = '支付宝－刷卡支付';
                    checkItem8 = data.payment[index].pay_rate;
                } else if(data.payment[index].pay_type==9){
                    payTypeName = '支付宝－JS支付';
                    checkItem9 = data.payment[index].pay_rate;
                }else if (data.payment[index].pay_type == 101) {
                    payTypeName = '微信－扫码支付';
                    checkItem1 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 102) {
                    payTypeName = '微信－刷卡支付';
                    checkItem2 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 103) {
                    payTypeName = '微信－公众账号支付';
                    checkItem3 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 104) {
                    payTypeName = '微信－APP支付';
                    checkItem4 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 107) {
                    payTypeName = '支付宝－扫码支付';
                    checkItem7 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 108) {
                    payTypeName = '支付宝－刷卡支付';
                    checkItem8 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 109) {
                    payTypeName = '支付宝－JS支付';
                    checkItem9 = data.payment[index].pay_rate;
                }
                if (data.auth_status == 2 && (data.payment[index].activated_status == 1 || data.payment[index].activated_status==3)) {
                    activatedName = '未激活';
                    if(data.bk_id==1) {
                        activatedHtml = "<a href='javascript:;' id=" + "td_" + data.payment[index].pay_type + " onclick='activatedMchInletStatus(" + data.mch_id + "," + data.payment[index].pay_type + ")'>激活</a >"
                    }
                    // 新逻辑，即使是审核驳回，如果该用户有激活状态的费率，也要现实激活状态
                } else if ((data.auth_status == 2 || data.auth_status == 3) && data.payment[index].activated_status == 2) {
                    activatedName = '激活状态';
                    var data_url='/bank/inlet/mch/close';
                    if(data.bk_id==1) {
                        activatedHtml = "<a href='javascript:;' onclick=rateClose('" + data_url + "'," + data.mch_id + "," + data.payment[index].pay_type + ",'" + payTypeName + "')>关闭</a >"
                    }
                } else if (data.payment[index].activated_status == 3){
                    activatedName = '修改中';
                    activatedHtml = "<span><a></a ></span>"
                }else {
                    activatedName = '未激活';
                    activatedHtml = "<span><a></a ></span>"
                }

                if(data.payment[index].activated_status == 1){
                    activatedName = '未激活';
                } else if(data.payment[index].activated_status == 2){
                    status_index++
                    activatedName = '激活状态';
                    var data_url='/bank/inlet/mch/close';
                    if(data.bk_id==1) {
                        activatedHtml = "<a href='javascript:;' onclick=rateClose('" + data_url + "'," + data.mch_id + "," + data.payment[index].pay_type + ",'" + payTypeName + "')>关闭</a >"
                    }
                } else if(data.payment[index].activated_status == 3){
                    status_index++;
                    activatedName = '修改中';
                }else{
                    activatedName = '未激活';
                }

                payHtml = payHtml + "<div class='col-md-5 col-sm-5'>" + payTypeName + "</div>";
                if(data.payment[index].pay_type>100){
                    payHtml = payHtml + "<div class='col-md-3 col-sm-3'>" + data.payment[index].pay_rate + "‰ (D0) </div>";
                }else{
                    payHtml = payHtml + "<div class='col-md-3 col-sm-3'>" + data.payment[index].pay_rate + "‰ (D1) </div>";
                }
                payHtml = payHtml + "<div class='col-md-2 col-sm-2' class='activeName' id='"+ "act_" + data.payment[index].pay_type +"'>" + activatedName + "</div>";
                payHtml = payHtml + "<div class='col-md-2 col-sm-2' class='activated'>" + activatedHtml + "</div>";
            }

            if(status_index == 0){
                $("#tr_"+value).children().eq(3).html('未激活');
            }
            var role=getRole(value,'mch');
            var roleHtml=''
            if(!$.isEmptyObject(role)){
                if(role.wx != null){
                    roleHtml+='<div class="role-box col-md-12">微信支付D0提现手续费： '+role.wx+'</div>';
                }
                if(role.alipay != null){
                    roleHtml+='<div class="role-box col-md-12">支 付 宝 D0提现手续费： '+role.alipay+'</div>';
                }
            }
            if(data.subsidize_info){
                if(data.subsidize_info.weixin != null ){
                    roleHtml+='<div class="role-box col-md-12">微信支付手续费补贴： '+data.subsidize_info.weixin+'%</div>';
                }
                if(data.subsidize_info.alipay != null ){
                    roleHtml+='<div class="role-box col-md-12">支 付 宝 手续费补贴： '+data.subsidize_info.alipay+'%</div>';
                }
            }
            /*-------------------风控操作-----------------------*/
            if(data.balance_status != 1 ){
                roleHtml += '<div class="role-box col-md-12">' +
                            '<span class="m-right-5">结算账户状态：正常</span>' ;
                if(data.bk_id==1) {
                    roleHtml +='<a href="javascript:;" class="m-left-5" _params={"role_id":"' + value + '","role_type":"cs","platform":"1","action":"close"} data-click="settleOperate">冻结</a> ' ;
                }
                roleHtml +='</div>';
            }else{
                roleHtml += '<div class="role-box col-md-12">' +
                            '<span class="m-right-5">结算账户状态：系统冻结</span>' ;
                if(data.bk_id==1) {
                    roleHtml +='<a href="javascript:;" class="m-left-5" _params={"role_id":"' + value + '","role_type":"cs","platform":"","action":"open"} data-click="settleOperate">恢复</a> ' ;
                }
                roleHtml +='</div>';
            }
            /*-------------------信用卡操作-----------------------*/
            if(data.credit_status){
                if(data.credit_status.weixin != 1 ){
                    roleHtml += '<div class="role-box col-md-12">' +
                                '<span class="m-right-5">微信支付信用卡支付权限：正常</span>' ;
                        if(data.bk_id==1) {
                            roleHtml += '<a href="javascript:;" class="m-left-5" _params={"role_id":"'+value+'","role_type":"cs","platform":"weixin","action":"close"} data-click="creditOperate">关闭</a> '
                        }
                    roleHtml +='</div>';
                }else{
                    roleHtml += '<div class="role-box col-md-12">' +
                                '<span class="m-right-5">微信支付信用卡支付权限：已关闭</span>' ;
                        if(data.bk_id==1) {
                            roleHtml += '<a href="javascript:;" class="m-left-5" _params={"role_id":"'+value+'","role_type":"cs","platform":"weixin","action":"open"} data-click="creditOperate">开启</a> '
                        }
                    roleHtml +='</div>';
                }
                if(data.credit_status.alipay != 1 ){
                    roleHtml += '<div class="role-box col-md-12">' +
                                '<span class="m-right-5">支 付 宝 信用卡支付权限：正常</span>' ;
                        if(data.bk_id==1) {
                            roleHtml += '<a href="javascript:;" class="m-left-5" _params={"role_id":"'+value+'","role_type":"cs","platform":"alipay","action":"close"} data-click="creditOperate">关闭</a> '
                        }
                    roleHtml +='</div>';
                }else{
                    roleHtml += '<div class="role-box col-md-12">' +
                                '<span class="m-right-5">支 付 宝 信用卡支付权限：已关闭</span>' ;
                        if(data.bk_id==1) {
                            roleHtml += '<a href="javascript:;" class="m-left-5" _params={"role_id":"'+value+'","role_type":"cs","platform":"alipay","action":"open"} data-click="creditOperate">开启</a> '
                        }
                    roleHtml +='</div>';
                }
            }

            appendHtml = appendHtml + "<div class='row zfBox' id='tabs'>";
            appendHtml = appendHtml + "<span>";
            appendHtml = appendHtml + "<ul class='col-md-12 col-sm-12'>";
            appendHtml = appendHtml + "<li class='col-md-4 col-sm-4 leftLine' id='payType' onclick='openPayTab()'>支付类型</li>";
            appendHtml = appendHtml + "<li class='col-md-4 col-sm-4 ' id='mchType' onclick='openMchTab()'>门店信息</li>";
            appendHtml = appendHtml + "<li class='col-md-4 col-sm-4 ' id='addType' onclick='openAddType()'>门店配置</li>";
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
                } else {
                    authHtml = authHtml + "<div><span>" + data.auth_info[auth_index].auth_at + " " + data.auth_info[auth_index].comment + " " + data.auth_info[auth_index].auth_user + "</span></div>";
                }
            }

            data.activated_info.sort(valueSort('desc', 'activated_at'));
            for (var activated_index=0; activated_index < data.activated_info.length; activated_index++){
                if(data.activated_info[activated_index].payment_type==1){
                    payTypeName = '微信－扫码支付';
                }else if(data.activated_info[activated_index].payment_type==2){
                    payTypeName = '微信－刷卡支付';
                }else if(data.activated_info[activated_index].payment_type==3){
                    payTypeName = '微信－公众号支付';
                }else if(data.activated_info[activated_index].payment_type==4){
                    payTypeName = '微信－APP支付';
                }else if(data.activated_info[activated_index].payment_type==5){
                    payTypeName = '微信－H5支付';
                }else if(data.activated_info[activated_index].payment_type==7){
                    payTypeName = '支付宝－扫码支付';
                }else if(data.activated_info[activated_index].payment_type==8){
                    payTypeName = '支付宝－刷卡支付';
                }else if(data.activated_info[activated_index].payment_type==9){
                    payTypeName = '支付宝－JS支付';
                }if(data.activated_info[activated_index].payment_type==11){
                    payTypeName = '围餐-微信－扫码支付';
                }else if(data.activated_info[activated_index].payment_type==12){
                    payTypeName = '围餐-微信－刷卡支付';
                }else if(data.activated_info[activated_index].payment_type==13){
                    payTypeName = '围餐-微信－公众号支付';
                }else if(data.activated_info[activated_index].payment_type==101){
                    payTypeName = 'D0-微信－扫码支付';
                }else if(data.activated_info[activated_index].payment_type==102){
                    payTypeName = 'D0-微信－刷卡支付';
                }else if(data.activated_info[activated_index].payment_type==103){
                    payTypeName = 'D0-微信－公众号支付';
                }else if(data.activated_info[activated_index].payment_type==104){
                    payTypeName = 'D0-微信－APP支付';
                }else if(data.activated_info[activated_index].payment_type==105){
                    payTypeName = 'D0-微信－H5支付';
                }else if(data.activated_info[activated_index].payment_type==107){
                    payTypeName = 'D0-支付宝－扫码支付';
                }else if(data.activated_info[activated_index].payment_type==108){
                    payTypeName = 'D0-支付宝－刷卡支付';
                }else if(data.activated_info[activated_index].payment_type==109){
                    payTypeName = 'D0-支付宝－JS支付';
                }
                activateHtml = activateHtml + "<div><span>" + data.activated_info[activated_index].activated_at + " " + payTypeName + " " + data.activated_info[activated_index].comment + " " + data.activated_info[activated_index].activated_user + "</span></div>";
            }

            var download_qr_url_small = '/common/qrdownload?text=' + QR_SCAN_URL + '/r?m=' + data.mch_id + '&size=142&save_name=' + data.mch_shortname + '(' +  data.mch_id + ')' + '.jpg';
            var download_qr_url = '/common/qrdownload?text=' + QR_SCAN_URL + '/r?m=' + data.mch_id + '&size=258&save_name=' + data.mch_shortname + '(' +  data.mch_id + ')' + '.jpg';
            var download_qr_url_big = '/common/qrdownload?text=' + QR_SCAN_URL + '/r?m=' + data.mch_id + '&size=430&save_name=' + data.mch_shortname + '(' +  data.mch_id + ')' + '.jpg';

            qrCodeHtml = qrCodeHtml + "<span>";
            qrCodeHtml = qrCodeHtml + "<div class='modal fade' id='qrCode' tabindex='-1' role='dialog' aria-labelledby='myModalLabel' aria-hidden='true'>";
            qrCodeHtml = qrCodeHtml + "<div class='modal-dialog'>";
            qrCodeHtml = qrCodeHtml + "<div class='modal-content'>";
            qrCodeHtml = qrCodeHtml + "<div class='modal-header'>";
            qrCodeHtml = qrCodeHtml + "<button type='button' class='close' data-dismiss='modal' aria-hidden='true'>&times;</button> <h3 class='modal-title'>门店固定收款码</h3>";
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
                authMchStatusHtml = authMchStatusHtml + "<label>门店编号</label>";
                authMchStatusHtml = authMchStatusHtml + "<span>" + data.mch_id + qrCodeHtml + "</span>";
                authMchStatusHtml = authMchStatusHtml + "</div>";
                authMchStatusHtml = authMchStatusHtml + "<div>";
                // authMchStatusHtml = authMchStatusHtml + "<label>微信商户编号:</label>";
                //微信商户编号为空时
                if(data.wx_sub_mch_id != null){
                    authMchStatusHtml = authMchStatusHtml + "<label>微信商户编号";
                    if (data.rate == 1){
                        authMchStatusHtml = authMchStatusHtml + "(0费率)";
                    }
                    authMchStatusHtml = authMchStatusHtml + "</label>";
                    authMchStatusHtml = authMchStatusHtml + "<span>"+data.wx_sub_mch_id;
                    if (data.wx_use_parent == 2) {
                        authMchStatusHtml = authMchStatusHtml + "(商户)";
                    }
                    authMchStatusHtml = authMchStatusHtml + "</span>";
                }else{
                    authMchStatusHtml = authMchStatusHtml + "<label>微信商户编号</label><span>无</span>";
                }

                authMchStatusHtml = authMchStatusHtml + "</div>";
            }

            appendMchInfoHtml = appendHtml + "<span id='mchInfo'>";
            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>基本信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + authMchStatusHtml;
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>所属连锁商户</label><span>" + data.parent_name + "</span></div>";
            if(res.INTER_BANK){
                if(data.bk_type == 1){
                    appendMchInfoHtml = appendMchInfoHtml + "<div><label>所属银行</label><span>主银行</span></div>";
                }else if(data.bk_type == 2){
                    appendMchInfoHtml = appendMchInfoHtml + "<div><label>所属银行</label><span>" + data.bk_name + "</span></div>";
                }
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
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>门店简称</label><span>"+ data.parent_short_name+'<a style="text-decoration: none;">('+data.mch_shortname+")</a></span></div>";
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
            appendMchInfoHtml = appendMchInfoHtml + "<h4>门店基本信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>门店名称</label><span>" + data.mch_name + "</span></div>";
            if(data.district == null){
                data.district='';
            }
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>省份城市</label><span>"+ data.province + data.city +  data.district + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系地址</label><span>" + data.address + "</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>门店基本信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>身份证</label><span>" + data.id_card_no + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>身份证照片</label><span>";
            appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.id_card_img_f + "' target='_blank'><img src='" + data.id_card_img_f + "'/></a>";
            appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.id_card_img_b + "' target='_blank'><img src='" + data.id_card_img_b + "'/></a>";
            appendMchInfoHtml = appendMchInfoHtml + "</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>门店负责人信息</h4>"
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
                appendMchInfoHtml = appendMchInfoHtml + "<span><a href='" + data.license_img + "' target='_blank'><img style='width: 100px;height: 100px' src='" + data.license_img + "'/></a><span>";
                appendMchInfoHtml = appendMchInfoHtml + "</div>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list_lost'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>操作记录</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + authHtml;
            appendMchInfoHtml = appendMchInfoHtml + activateHtml;
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
        url: '/bank/inlet/cs/activated',
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
                $(tr + " td:nth-child(4)").html("已激活");
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
        url: '/bank/inlet/cs/batchActivated',
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
                $(tr + " td:nth-child(4)").html("已激活");
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

