/**
 * Created by xiezhigang on 16/10/17.
 */
tableBox = $("#dtPayInfo");
appendPayHtml = "";
appendMchInfoHtml = "";
function openNewTable(value) {
    if (document.getElementById("tabs")) {
        appendPayHtml = "";
        appendMchInfoHtml = "";
    }
    $.ajax({
        type: 'GET',
        data: {"dt_id": value},
        dataType: 'json',
        url: '/chain/inlet/chain/detail'
    }).done(function (res) {
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
            var checkItem7 = "";
            var checkItem8 = "";
            var checkItem9 = "";
            var toUrl = "";
            var bt_name = "";
            var licenseNum = "";
            var licenseStartDate = "";
            var licenseEndDate = "";
            var licensePeriod = "";
            var licenseScope = "";
            var licenseImgOld = data.license_img;

            if (data.balance_type == 1) {
                bt_name = '企业';
            } else if (data.balance_type == 2) {
                bt_name = '个人';
            }

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
                } else if (data.payment[index].pay_type == 7) {
                    payTypeName = '支付宝－扫码支付';
                    checkItem7 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 8) {
                    payTypeName = '支付宝－刷卡支付';
                    checkItem8 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 9) {
                    payTypeName = '支付宝－JS支付';
                    checkItem9 = data.payment[index].pay_rate;
                }

                if (data.payment[index].activated_status == 1) {
                    activatedName = '未激活';
                } else if (data.payment[index].activated_status == 2) {
                    activatedName = '激活状态';
                } else if (data.payment[index].activated_status == 3) {
                    activatedName = '修改中';
                }

                if (data.balance_type == 1) {
                    bt_name = '企业';
                } else if (data.balance_type == 2) {
                    bt_name = '个人';
                }
                payHtml = payHtml + "<div class='col-md-8 col-sm-8'>" + payTypeName + "</div>";
                payHtml = payHtml + "<div class='col-md-2 col-sm-2'>" + data.payment[index].pay_rate + "‰ </div>";
                payHtml = payHtml + "<div class='col-md-2 col-sm-2'>" + activatedName + "</div>"
            }

            if (data.auth_status == 2 || data.auth_status == 3) {
                toUrl = '/chain/inlet/chain/modify?dt_id=' + data.dt_id + '&email=' + data.email
                    + '&address=' + data.address + '&province=' + data.province + '&city=' + data.city + '&contact=' + data.contact
                    + '&mobile=' + data.mobile + '&balanceType=' + data.balance_type + '&balanceName='
                    + data.balance_name + '&bankNo=' + data.bank_no + '&bankName=' + data.bank_name + '&balanceNo=' + data.balance_account
                    + '&idCard=' + data.id_card_no + '&imgCardFrontOld=' + imgCardFrontOld
                    + '&imgCardBackOld=' + imgCardBackOld + '&checkItem1=' + checkItem1 + '&checkItem2=' + checkItem2
                    + '&checkItem3=' + checkItem3 + '&checkItem4=' + checkItem4 + '&checkItem7=' + checkItem7 + '&checkItem8=' + checkItem8
                    + '&checkItem9=' + checkItem9 + '&dtName=' + data.dt_name;
                // +'&licenseNum='+data.license_num
                // +'&licenseStartDate='+data.license_start_date
                // +'&licenseEndDate='+data.license_end_date
                // +'&licensePeriod='+data.license_period
                // +'&licenseScope='+data.license_scope
                // +'&licenseImgOld='+licenseImgOld;

                if (data.service_phone == null) {
                    toUrl += '&service_phone=' + data.mobile;
                } else {
                    toUrl += '&service_phone=' + data.service_phone;
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
                if (data.license_scope) {
                    toUrl += '&licenseScope=' + data.license_scope;
                }
                toUrl += '&licenseImgOld=' + data.license_img;
                modifyHtml = modifyHtml + "<a class='btn btn-default btnTop' href=" + toUrl + ">修改</a>";
            }


            appendHtml = appendHtml + "<div class='row zfBox' id='tabs'>";
            appendHtml = appendHtml + "<span>";
            appendHtml = appendHtml + "<ul class='col-md-12 col-sm-12'>";
            appendHtml = appendHtml + "<li class='col-md-6 col-sm-6 leftLine' id='payType' onclick='openPayTab()'>支付类型</li>";
            appendHtml = appendHtml + "<li class='col-md-6 col-sm-6 ' id='mchType' onclick='openMchTab()'>商户信息</li>";
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

            for (var auth_index = 0; auth_index < data.auth_info.length; auth_index++) {
                if (data.auth_info[auth_index].auth_status == 3 || data.auth_info[auth_index].auth_status == 7) {
                    var target_index = 'auth_' + auth_index;
                    authHtml = authHtml + "<div><span>" + data.auth_info[auth_index].auth_at + "<a data-toggle='modal' data-target=" + "#" + target_index + ">" + data.auth_info[auth_index].comment + "</a></span></div>";

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
                    authHtml = authHtml + "<div><span>" + data.auth_info[auth_index].auth_at + " " + data.auth_info[auth_index].comment + "</span></div>";
                }

            }

            for (var activated_index = 0; activated_index < data.activated_info.length; activated_index++) {
                if (data.activated_info[activated_index].payment_type == 1) {
                    payTypeName = '微信－扫码支付';
                } else if (data.activated_info[activated_index].payment_type == 2) {
                    payTypeName = '微信－刷卡支付';
                } else if (data.activated_info[activated_index].payment_type == 3) {
                    payTypeName = '微信－公众号支付';
                } else if (data.activated_info[activated_index].payment_type == 4) {
                    payTypeName = '微信－APP支付';
                } else if (data.activated_info[activated_index].payment_type == 7) {
                    payTypeName = '支付宝－扫码支付';
                } else if (data.activated_info[activated_index].payment_type == 8) {
                    payTypeName = '支付宝－刷卡支付';
                } else if (data.activated_info[activated_index].payment_type == 9) {
                    payTypeName = '支付宝－JS支付';
                }
                activateHtml = activateHtml + "<div><span>" + data.activated_info[activated_index].activated_at + " " + payTypeName + " " + data.activated_info[activated_index].comment + "</span></div>";
            }

            appendMchInfoHtml = appendHtml + "<span id='mchInfo'>";
            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>基本信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>连锁商户编号</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.dt_id;
            if (data.rate == 1){
                appendMchInfoHtml = appendMchInfoHtml + "(0费率)";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</span>"
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            // appendMchInfoHtml = appendMchInfoHtml + "<div><label>微信商户编号</label><span>" + wx + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>所属渠道商</label><span>" + data.parent_name + "</span></div>";
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
            appendMchInfoHtml = appendMchInfoHtml + "<h4>连锁商户基本信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>连锁商户名称</label><span>" + data.dt_name + "</span></div>";
            if(data.district == null){
                data.district='';
            }
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>省份城市</label><span>"+ data.province + data.city +  data.district + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系地址</label><span>" + data.address +"</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>连锁商户负责人信息</h4>";
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
            appendMchInfoHtml = appendMchInfoHtml + modifyHtml;
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "</span>";
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            tableBox.html(appendPayHtml);
        } else {

        }
    }).fail(function () {
        alert("服务器繁忙");
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