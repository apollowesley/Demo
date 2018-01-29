/**
 * Created by xiezhigang on 16/10/17.
 */
tableBox = $("#mchPayInfo");
appendPayHtml = "";
appendMchInfoHtml = "";
appendAddressHtml = "";
function openNewTable(value) {
    if (document.getElementById("tabs")){
        appendPayHtml = "";
        appendMchInfoHtml = "";
        appendAddressHtml = "";
    }
    $.ajax({
        type: 'GET',
        data: {"mch_id": value},
        dataType: 'json',
        url: '/chain/inlet/cs/detail'
    }).done(function(res){
        if (res.code == '200') {
            var data = res.data;
            window.mch_id = data.mch_id;
            var imgCardFrontOld = data.id_card_img_f;
            var imgCardBackOld = data.id_card_img_b;
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
            var checkItem7 = "";
            var checkItem8 = "";
            var checkItem9 = "";
            var toUrl = "";
            var authMchStatusHtml = "";
            var bt_name = "";

            var licenseNum = "";
            var licenseStartDate = "";
            var licenseEndDate = "";
            var licensePeriod = "";
            var licenseScope = "";

            if(data.balance_type==1){
                bt_name = '企业';
            }else if(data.balance_type==2){
                bt_name = '个人';
            }

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
                }else if(data.payment[index].pay_type==4){
                    payTypeName = '微信－APP支付';
                    checkItem4 = data.payment[index].pay_rate;
                }else if(data.payment[index].pay_type==7){
                    payTypeName = '支付宝－扫码支付';
                    checkItem7 = data.payment[index].pay_rate;
                }else if(data.payment[index].pay_type==8){
                    payTypeName = '支付宝－刷卡支付';
                    checkItem8 = data.payment[index].pay_rate;
                }else if(data.payment[index].pay_type==9){
                    payTypeName = '支付宝－JS支付';
                    checkItem9 = data.payment[index].pay_rate;
                }
                if(data.payment[index].activated_status==1){
                    activatedName = '未激活';
                }else if(data.payment[index].activated_status==2){
                    activatedName = '激活状态';
                }else if(data.payment[index].activated_status==3){
                    activatedName = '修改中';
                }
                payHtml = payHtml + "<div class='col-md-8 col-sm-8'>" + payTypeName +"</div>";
                payHtml = payHtml + "<div class='col-md-2 col-sm-2'>" + data.payment[index].pay_rate + "‰ </div>";
                payHtml = payHtml + "<div class='col-md-2 col-sm-2'>" + activatedName + "</div>"
            }
            if (data.auth_status==2 || data.auth_status==3){
                toUrl = '/chain/inlet/cs/modify?mch_id='+data.mch_id+'&imgCardFrontOld='+imgCardFrontOld
                    +'&imgCardBackOld='+imgCardBackOld+'&mchShortName='+data.mch_shortname+'&mchName='+data.mch_name
                    +'&jobType='+data.u_ind_code +'&email='+data.email+'&address='+data.address
                    +'&province='+data.province+'&city='+data.city+'&contact='+data.contact+'&mobile='+data.mobile
                    +'&servicePhone='+data.service_phone+'&balanceType='+data.balance_type
                    +'&balanceName='+data.balance_name+'&bankNo='+data.bank_no+'&bankName='+data.bank_name
                    +'&balanceNo='+data.balance_account+'&idCard='+data.id_card_no+'&industryName='+data.industry_name
                    +'&checkItem1='+checkItem1+'&checkItem2='+checkItem2+'&checkItem3='+checkItem3+'&checkItem4='+checkItem4
                    +'&checkItem7='+checkItem7+'&checkItem8='+checkItem8+'&checkItem9='+checkItem9;
                    // +'&licenseNum='+data.license_num
                    // +'&licenseStartDate='+data.license_start_date
                    // +'&licenseEndDate='+data.license_end_date
                    // +'&licensePeriod='+data.license_period
                    // +'&licenseScope='+data.license_scope
                    // +'&licenseImgOld='+licenseImgOld;
                if (data.license_num){
                    toUrl += '&licenseNum='+data.license_num;
                }
                if (data.license_start_date){
                    toUrl += '&licenseStartDate='+data.license_start_date;
                }
                if (data.license_end_date){
                    toUrl += '&licenseEndDate='+data.license_end_date;
                }
                if (data.license_period){
                    toUrl += '&licensePeriod='+data.license_period;
                }
                if (data.license_scope){
                    toUrl += '&licenseScope='+data.license_scope;
                }
                toUrl += '&licenseImgOld='+data.license_img;
                modifyHtml = modifyHtml + "<a class='btn btn-default btnTop' href="+toUrl+">修改</a>";
            }

            appendHtml = appendHtml + "<div class='row zfBox' id='tabs'>";
            appendHtml = appendHtml + "<span>";
            appendHtml = appendHtml + "<ul class='col-md-12 col-sm-12'>";
            appendHtml = appendHtml + "<li class='col-md-4 col-sm-4 leftLine' id='payType' onclick='openPayTab()'>支付类型</li>";
            appendHtml = appendHtml + "<li class='col-md-4 col-sm-4 ' id='mchType' onclick='openMchTab()'>商户信息</li>";
            appendHtml = appendHtml + "<li class='col-md-4 col-sm-4 ' id='addType' onclick='openAddType()'>商户配置</li>";
            appendHtml = appendHtml + "</ul>";
            appendHtml = appendHtml + "</span>";

            appendPayHtml = appendPayHtml + appendHtml;
            appendPayHtml = appendPayHtml + "<span id='payRate'>";
            appendPayHtml = appendPayHtml + "<div class='col-md-12 col-sm-12'>";
            appendPayHtml = appendPayHtml + "<div class='col-md-8 col-sm-8'>" + data.mch_name + "</div>";
            appendPayHtml = appendPayHtml + "<div class='col-md-2 col-sm-2'>费率</div>";
            appendPayHtml = appendPayHtml + "<div class='col-md-2 col-sm-2'>状态</div>";
            appendPayHtml = appendPayHtml + "</div>";
            appendPayHtml = appendPayHtml + "<span>";
            appendPayHtml = appendPayHtml + payHtml;
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
            appendAddressHtml = appendAddressHtml + "<div><span class='add-callback' id=" + "add-callback-" +value+ ">"+callback+"</span><a data-toggle='modal' data-target="+ "#addressModal-" + value +">修改</a></div>";
            appendAddressHtml = appendAddressHtml + "<div>针对商户需要使用ULINE生成的商户固定支付二维码,且需要交易回调时,在此填写需要回调的URL<br>若无此需求,不需要填写</div>";
            appendAddressHtml = appendAddressHtml + "</div>";

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


            for (var auth_index=0; auth_index < data.auth_info.length; auth_index++){
                if (data.auth_info[auth_index].auth_status == 3 || data.auth_info[auth_index].auth_status == 7) {
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

            for (var activated_index=0; activated_index < data.activated_info.length; activated_index++){
                if(data.activated_info[activated_index].payment_type==1){
                    payTypeName = '微信－扫码支付';
                }else if(data.activated_info[activated_index].payment_type==2){
                    payTypeName = '微信－刷卡支付';
                }else if(data.activated_info[activated_index].payment_type==3){
                    payTypeName = '微信－公众号支付';
                }else if(data.activated_info[activated_index].payment_type==4){
                    payTypeName = '微信－APP支付';
                }else if(data.activated_info[activated_index].payment_type==7){
                    payTypeName = '支付宝－扫码支付';
                }else if(data.activated_info[activated_index].payment_type==8){
                    payTypeName = '支付宝－刷卡支付';
                }else if(data.activated_info[activated_index].payment_type==9){
                    payTypeName = '支付宝－JS支付';
                }
                activateHtml = activateHtml + "<div><span>"+ data.activated_info[activated_index].activated_at+ " " + payTypeName+ " " +data.activated_info[activated_index].comment+"</span></div>";
            }

            qrCodeHtml = qrCodeHtml + "<span>";
            qrCodeHtml = qrCodeHtml + "<div class='modal fade' id='qrCode' tabindex='-1' role='dialog' aria-labelledby='myModalLabel' aria-hidden='true'>";
            qrCodeHtml = qrCodeHtml + "<div class='modal-dialog'>";
            qrCodeHtml = qrCodeHtml + "<div class='modal-content'>";
            qrCodeHtml = qrCodeHtml + "<div class='modal-header'>";
            qrCodeHtml = qrCodeHtml + "<button type='button' class='close' data-dismiss='modal' aria-hidden='true'>&times;</button>";
            qrCodeHtml = qrCodeHtml + "</div>";
            qrCodeHtml = qrCodeHtml + "<div class='modal-body'><div id='mch_qrCode'></div><p class='code'>商户固定收款二维码</p></div>";
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

                authMchStatusHtml = authMchStatusHtml + "<label>微信商户编号";
                if (data.rate == 1){
                    authMchStatusHtml = authMchStatusHtml + "(0费率)";
                }
                authMchStatusHtml = authMchStatusHtml + "</label>";

                authMchStatusHtml = authMchStatusHtml + "<span>"+data.wx_sub_mch_id;
                if (data.mch_wx_use_parent == 2) {
                    authMchStatusHtml = authMchStatusHtml + "(渠道商)";
                }
                authMchStatusHtml = authMchStatusHtml + "</span>";
                authMchStatusHtml = authMchStatusHtml + "</div>";
            }

            appendMchInfoHtml = appendHtml + "<span id='mchInfo'>";
            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>基本信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + authMchStatusHtml;
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>所属渠道商</label><span>" + data.dt_name +"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>联系信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系人</label><span>" + data.contact +"</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系电话</label><span>" + data.mobile + "</span></div>";
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
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>省份城市</label><span>" + data.province + data.city + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系地址</label><span>" + data.address +"</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>商户负责人信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>身份证号码</label><span>" + data.id_card_no + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>身份证照片</label><span>";
            appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.id_card_img_f + "' target='_blank'><img src='" + data.id_card_img_f + "'/></a>";
            appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.id_card_img_b + "' target='_blank'><img src='" + data.id_card_img_b + "'/></a>";
            appendMchInfoHtml = appendMchInfoHtml + "</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>商户执照信息</h4>"
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>营业执照注册号</label>";
            if (data.license_num) {
                appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.license_num + "</span>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>营业开始时间</label>";
            if (data.license_start_date) {
                appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.license_start_date + "</span>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>营业结束时间</label>";
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
                appendMchInfoHtml = appendMchInfoHtml + "<label>营业执照照片</label>";
                appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.license_img + "' target='_blank'><img style='width: 100px;height: 100px' src='" + data.license_img + "'/></a>";
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
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + modifyHtml;
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            tableBox.html(appendPayHtml);
                        //调用函数
            // getAddress();
        } else {

        }
    }).fail(function(){
        alert("服务器繁忙");
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
        url :'/chain/inlet/cs/callbackurl',
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

