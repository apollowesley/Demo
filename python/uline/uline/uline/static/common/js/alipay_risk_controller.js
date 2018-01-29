
;(function($){

    var urlHeader=window.location.href.split('/')[3];

    $('#updateModal').find('input[type="checkbox"]').click(function(){
        if($(this).is(':checked')){
            $(this).attr('checked','checked');
        }else{
            $(this).removeAttr('checked');
        }
    });

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
    };

    //公用请求方法
    function ajaxResponsePromise(request_url,request_data,request_type){
        if(request_type == 'POST'){
            var xsrf=getCookie("_xsrf");
        }

        return $.ajax({
            headers: {"X-XSRFToken":xsrf},
            type:request_type || 'GET',
            url:request_url,
            data:request_data,
            dataType:'json',
            error:function(){
                errorTip('网络出错，请重试');
            }
        })
    }

    function getCookie(name) {
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    }

    var riskServices={
        'getMchDetail':function(request_data){
            var params=request_data;
            var url='/'+urlHeader+'/risk/merchant/detail';
            return ajaxResponsePromise(url,params);
        },//商户风险信息详情
        'getTradeDetail':function(request_data){
            var params=request_data;
            var url='/'+urlHeader+'/risk/trade/detail';
            return ajaxResponsePromise(url,params);
        },//交易风险信息详情
        'sendTradeDeal':function(request_data){
            var params=request_data;
            var url='/'+urlHeader+'/risk/trade/deal';
            return ajaxResponsePromise(url,params);
        },//交易风险信息处理
        'getRateList':function(request_data){
            var params=request_data;
            var url='/'+urlHeader+'/risk/merchant/payments';
            return ajaxResponsePromise(url,params);
        },//获取费率列表
        'settleOperate':function(request_data){
            var params=request_data;
            var url='/'+urlHeader+'/risk/settle/operate';
            return ajaxResponsePromise(url,params,"POST");
        },//账户冻结、打开操作
        'creditOperate':function(request_data){
            var params=request_data;
            var url='/'+urlHeader+'/risk/credit/operate';
            return ajaxResponsePromise(url,params,"POST");
        },//信用卡支付权限操作
    };


    //click
    $(document).on('click','[data-click]',function(e) {
        e.stopPropagation();
        e.preventDefault();

        var self = $(this),
            name = $(this).data('click');

        switch (name) {

            case 'getMchDetail':
                var _params={
                    risk_id:self.attr('risk-id')
                };
                riskServices.getMchDetail(_params).then(function(res){
                    if(res.code==200){
                        for (_key in res.data){
                            $('[data-key="'+_key+'"]').html(res.data[_key]);
                        }
                        if(res.data.source == 'alipay'){
                            $('#source').html('支付宝');
                        }else if(res.data.source == 'wx'){
                            $('#source').html('微信');
                        }
                        if(res.data.has_risk == 0){
                            $('#has-risk').html('无风险');
                        }else if(res.data.has_risk >0 ){
                            $('#has-risk').html('有风险');
                        }
                        $('#infoModal').modal('show');
                    }
                });
                break;

            case 'getTradeDetail':
                var _params={
                    risk_id:self.attr('risk-id')
                };
                riskServices.getTradeDetail(_params).then(function(res){
                    if(res.code==200){
                        for (_key in res.data){
                            $('[data-key="'+_key+'"]').html(res.data[_key]);
                        }
                        if(res.data.platform == 'alipay'){
                            $('#platform').html('支付宝');
                        }else if(res.data.platform == 'wx'){
                            $('#platform').html('微信');
                        }
                        if(res.data.status == 1){
                            $('#status').html('未处理');
                        }else if(res.data.status == 2 ){
                            $('#status').html('已处理');
                        }else if(res.data.status == 3 ){
                            $('#status').html('忽略');
                        }
                        $('#infoModal').modal('show');
                    }
                });
                break;

            case 'getRateList':
                var _params={
                    merchant_id:self.attr('merchant-id'),
                };
                $('#updateModal').attr('risk-id',self.attr('risk-id'));
                riskServices.getRateList(_params).then(function(res){
                    if(res.code==200){
                        var rateList=res.data.payments;
                        var settleList=res.data.settle_info;
                        var html='',_html='';
                        for(var i=0;i<rateList.length;i++){
                            html += '<tr>' +
                                    '<td><input type="checkbox" value="'+rateList[i].uline_payment_code+'" ' ;
                            if(rateList[i].activated_status==1){
                                html += 'disabled="disabled" checked="checked"'
                            }
                            html +=' /></td>' +
                                    '<td>'+AVAILABLE_PAYMENTS[rateList[i].uline_payment_code]+'</td>' +
                                    '</tr>';
                        }
                        if(settleList){
                            _html += '<div class="float-left risk-m-right">\n' ;
                            _html += '<input type="checkbox" value="1" ' ;
                            if(settleList==1){
                                _html += 'disabled="disabled" checked="checked"'
                            }
                            _html +=   '/>冻结结算账户\n' ;
                            _html += '</div>'
                        }
                        $('.risk-rate-list').html(html);
                        $('.risk-freeze-account').html(_html);
                        $('#updateModal').modal('show');
                    }
                });
                break;

            case 'sendTradeDeal':
                var _params={
                    handle_type:'deal',
                    risk_id:$('#updateModal').attr('risk-id'),
                    close_payments:[],
                    freeze_account:'',
                };
                $('.risk-rate-list input').each(function(){
                    if($(this).is(':checked')){
                        _params.close_payments.push($(this).val());
                    }
                });
                if($('.risk-freeze-account input').is(':checked')){
                    _params.freeze_account='1';
                }
                _params.close_payments=_params.close_payments.join(",");
                dealResult(_params);
                break;

            case 'dealIgnore':
                var _params={
                    handle_type:'ignore',
                    risk_id:self.attr('risk-id'),
                    close_payments:'',
                    freeze_account:'',
                };
                dealResult(_params);
                break;

            case 'settleOperate':
                var _params=self.attr('_params');
                _params=eval('(' + _params + ')');
                riskServices.settleOperate(_params).then(function(res){
                    if(res.code==200){
                        errorTip(res.msg);
                        setTimeout(function(){
                            judgeStatus(_params.role_id);
                            openNewTable(_params.role_id,1);
                        },1000);
                    }else{
                        errorTip(res.msg);
                    }
                });
                break;

            case 'creditOperate':
                var _params=self.attr('_params');
                _params=eval('(' + _params + ')');
                if(_params.action=='close'){
                    $('body').ulaiberLoading({
                        loadingTitle:'确认关闭信用卡支付权限吗？',
                        loadingText:'关闭之后该商户的顾客将无法使用信用卡付款。',
                        loadingType:'comfirm',
                        sureFunction:function(){
                            creditSuccessFn(_params);
                        }
                    });
                }else{
                    creditSuccessFn(_params);
                }
                break;



        }
    });

    function creditSuccessFn(_params){
        riskServices.creditOperate(_params).then(function(res){
            if(res.code==200){
                errorTip(res.msg);
                setTimeout(function(){
                    judgeStatus(_params.role_id);
                    openNewTable(_params.role_id,1);
                },1000);
            }else{
                errorTip(res.msg);
            }
        });
    }

    function dealResult(_params){
        riskServices.sendTradeDeal(_params).then(function(res){
            if(res.code==200){
                $('#updateModal').modal('hide');
                errorTip('交易风险处理成功');
                setTimeout(function(){
                    window.location.reload();
                },1500)
            }else{
                errorTip('交易风险处理失败，请重试');
            }
        });
    }






})(jQuery);
