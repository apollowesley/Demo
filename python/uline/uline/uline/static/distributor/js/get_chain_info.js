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
        data: {"chain_id": value},
        dataType: 'json',
        url: '/dist/inlet/chain/detail',
        complete:function(){
            getWxPayConfig(value,true);
        }
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
            var checkItem7 = "";
            var checkItem8 = "";
            var checkItem9 = "";
            var checkItem101 = "";
            var checkItem102 = "";
            var checkItem103 = "";
            var checkItem104 = "";
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

            if (data.balance_type == 1) {
                bt_name = '企业';
            } else if (data.balance_type == 2) {
                bt_name = '个人';
            }
            data.payment.sort(valueSort('asc','pay_type'));
            for (var index = 0; index < data.payment.length; index++) {
                paymentStr+='checkItem'+data.payment[index].pay_type+':'+data.payment[index].pay_rate+',';
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
                } else if (data.payment[index].pay_type == 101) {
                    payTypeName = '微信－扫码支付';
                    checkItem101 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 102) {
                    payTypeName = '微信－刷卡支付';
                    checkItem102 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 103) {
                    payTypeName = '微信－公众账号支付';
                    checkItem103 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 104) {
                    payTypeName = '微信－APP支付';
                    checkItem104 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 107) {
                    payTypeName = '支付宝－扫码支付';
                    checkItem107 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 108) {
                    payTypeName = '支付宝－刷卡支付';
                    checkItem108 = data.payment[index].pay_rate;
                } else if (data.payment[index].pay_type == 109) {
                    payTypeName = '支付宝－JS支付';
                    checkItem109 = data.payment[index].pay_rate;
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
                payHtml = payHtml + "<div class='col-md-6 col-sm-6'>" + payTypeName + "</div>";
                if(data.payment[index].pay_type>100){
                    payHtml = payHtml + "<div class='col-md-4 col-sm-4'>" + data.payment[index].pay_rate + "‰ (D0) </div>";
                }else{
                    payHtml = payHtml + "<div class='col-md-4 col-sm-4'>" + data.payment[index].pay_rate + "‰ (D1) </div>";
                }
                payHtml = payHtml + "<div class='col-md-2 col-sm-2'>" + activatedName + "</div>"
            }

            var u_ind_name=data.u_ind_name.split('-');

            if (data.auth_status == 2 || data.auth_status == 3 || data.auth_status == 7 ) {
                toUrl = '/dist/inlet/chain/modify?chain_id=' + data.dt_id + '&email=' + data.email
                    + '&province=' + data.province + '&city=' + data.city + '&contact=' + data.contact
                    + '&mobile=' + data.mobile + '&balance_type=' + data.balance_type
                    + '&bank_no=' + data.bank_no + '&balance_account=' + data.balance_account
                    + '&imgCardFrontOld=' + imgCardFrontOld
                    + '&imgCardBackOld=' + imgCardBackOld + '&checkItem1=' + checkItem1 + '&checkItem2=' + checkItem2
                    + '&checkItem3=' + checkItem3 + '&checkItem4=' + checkItem4 + '&checkItem7=' + checkItem7 + '&checkItem8=' + checkItem8
                    + '&checkItem9=' + checkItem9 + '&checkItem101=' + checkItem101 + '&checkItem102=' + checkItem102
                    + '&checkItem103=' + checkItem103 + '&checkItem104=' + checkItem104 + '&checkItem107=' + checkItem107 + '&checkItem108=' + checkItem108
                    + '&checkItem109=' + checkItem109 + '&area=' + u_ind_name[0]+ '&cmbProvince=' + u_ind_name[1]
                    + '&cmbCity=' + u_ind_name[2] + '&cmbArea=' + u_ind_name[3]+ '&dtType=' + data.dt_type;
                if(!$.isEmptyObject(data.role)){
                    if(data.role.wx != null){
                        toUrl+='&wx=' + data.role.wx;
                    }
                    if(data.role.alipay != null){
                        toUrl+='&alipay=' + data.role.alipay;
                    }
                }
                if(data.wx_channel_id != ''){
                    toUrl += '&wx_channel_id=' + data.wx_channel_id;
                }


                if (data.service_phone == null) {
                    toUrl += '&service_phone=' + data.mobile;
                } else {
                    toUrl += '&service_phone=' + data.service_phone;
                }

                if (data.license_num) {
                    toUrl += '&license_num=' + data.license_num;
                }
                if (data.license_start_date) {
                    toUrl += '&license_start_date=' + data.license_start_date;
                }
                if (data.license_end_date) {
                    toUrl += '&licenseEndDate=' + data.license_end_date;
                }
                if (data.license_period) {
                    toUrl += '&licensePeriod=' + data.license_period;
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

                toUrl += '&licenseImgOld=' + data.license_img;
                modifyHtml = modifyHtml + "<a class='btn btn-default btnTop'  onclick=setRateCookie('"+paymentStr+"') href=" + toUrl + ">修改</a>";
            }
            if(!$.isEmptyObject(data.role)){
                if(data.role.wx != null){
                    payHtml+='<div class="role-box col-md-12">微信支付D0提现手续费： '+data.role.wx+'</div>';
                }
                if(data.role.alipay != null){
                    payHtml+='<div class="role-box col-md-12">支 付 宝 D0提现手续费： '+data.role.alipay+'</div>';
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


            /*-----------------------------------------------微信支付配置 start-----------------------------------------------------------*/

            appendAddressHtml = appendAddressHtml + appendHtml;
            appendAddressHtml = appendAddressHtml + "<div id='add-callback'>";
            appendAddressHtml = appendAddressHtml + "<p>开户邮件接收方</p>";
            appendAddressHtml = appendAddressHtml + "<div><span class='m-right-5'>" + data.activate_email_tag + "</span>";
            if(data.activated_status==2){
                appendAddressHtml = appendAddressHtml + "<a href='javascript:;' id='resend-email' onclick='resendActiveEmail("+value+");'>重新发送激活邮件</a></div>";
            }
            appendAddressHtml = appendAddressHtml + "</div>";
            appendAddressHtml += "<div class='wx-config-wrap' style='padding-top:50px;'></div>";
            $('#thisMchId').val(value);

            /*-----------------------------------------------微信支付配置 end-----------------------------------------------------------*/

            data.auth_info.sort(valueSort('desc', 'auth_at'));
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
                activateHtml = activateHtml + "<div><span>" + data.activated_info[activated_index].activated_at + " " + payTypeName + " " + data.activated_info[activated_index].comment + "</span></div>";
            }

            appendMchInfoHtml = appendHtml + "<span id='mchInfo'>";
            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";
            appendMchInfoHtml = appendMchInfoHtml + "<h4>基本信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>商户编号</label>";
            appendMchInfoHtml = appendMchInfoHtml + "<span>" + data.dt_id;
            if (data.rate == 1){
                appendMchInfoHtml = appendMchInfoHtml + "(0费率)";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</span>"
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div>";
            appendMchInfoHtml = appendMchInfoHtml + "<label>微信商户编号";
            if (data.rate == 1) {
                appendMchInfoHtml = appendMchInfoHtml + "(0费率)";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</label>";
            if(data.wx_sub_mch_id != null) {
                appendMchInfoHtml = appendMchInfoHtml + "<span>线下：" + data.wx_sub_mch_id;
                if(data.use_dine && data.use_dine==1){
                    appendMchInfoHtml = appendMchInfoHtml + "(围餐)";
                } else if (data.wx_use_parent == 2) {
                    appendMchInfoHtml = appendMchInfoHtml + "(渠道商)";
                }
                appendMchInfoHtml = appendMchInfoHtml + "</span>";
            }
            if(data.wx_app_sub_mch_id != null){
                appendMchInfoHtml = appendMchInfoHtml + "<span>线上：" + data.wx_app_sub_mch_id + "</span>";
            }
            if(data.wx_sub_mch_id == null && data.wx_app_sub_mch_id == null){
                appendMchInfoHtml = appendMchInfoHtml + "<span>无</span>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";
            if (data.dt_sub_name != null){
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>业务员</label><span>" + data.dt_sub_name + "</span></div>";
            }
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
            if(data.jd_sub_mch_id ){
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>京东商户号</label><span>" + data.jd_sub_mch_id + "</span></div>";
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
            if (data.service_phone == null) {
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>客服电话</label><span>" + data.mobile + "</span></div>";
            } else {
                appendMchInfoHtml = appendMchInfoHtml + "<div><label>客服电话</label><span>" + data.service_phone + "</span></div>";
            }
            appendMchInfoHtml = appendMchInfoHtml + "</div>";

            appendMchInfoHtml = appendMchInfoHtml + "<div class='col-md-12 col-sm-12 list'>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>商户基本信息</h4>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>商户名称</label><span>" + data.dt_name + "</span></div>";
            if(data.district == null){
                data.district='';
            }
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>省份城市</label><span>"+ data.province + data.city +  data.district + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>联系地址</label><span>" + data.address +"</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>商户负责人信息</h4>";
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
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>身份证</label><span>" + data.id_card_no + "</span></div>";
            appendMchInfoHtml = appendMchInfoHtml + "<div><label>身份证照片</label><span>";
            appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.id_card_img_f + "' target='_blank'><img src='" + data.id_card_img_f + "'/></a>";
            appendMchInfoHtml = appendMchInfoHtml + "<a href='" + data.id_card_img_b + "' target='_blank'><img src='" + data.id_card_img_b + "'/></a>";
            appendMchInfoHtml = appendMchInfoHtml + "</span></div>";

            appendMchInfoHtml = appendMchInfoHtml + "<h4>营业执照信息</h4>";
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

    _xsrf=$('input[name="_xsrf"]').val();
    $.ajax({
        type: 'POST',
        data: {
            "mch_id": value,
            'config_key': 'subscribe_appid',
            'config_value': 'sdasdfads',
            "_xsrf":_xsrf
        },
        dataType: 'json',
        url: '/dist/inlet/chain/wx_config'
    }).done(function(res){

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
function openAddType() {
    if (document.getElementById("payType") && document.getElementById("mchType") && document.getElementById("addType")){
        tableBox.html(appendAddressHtml);
    }
    $('#addType').addClass('leftLine').siblings().removeClass('leftLine');
}
openPayTab();
openMchTab();
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
        url: '/dist/inlet/chain/resend_active_email'
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