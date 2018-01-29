/**
 * Created by apple on 11/5/17.
 */

function rateClose(url,id,payment_type,title){
    var _params={};
    if(url == '/bank/inlet/dt/close' || url == '/inter_bank/inlet/dt/close'){
        var msg='<p style="text-align:left;">关闭之后渠道商下的商户将无法再使用'+title+'</p>';
        _params={dt_id:id,payment_type:payment_type};
    }else if(url == '/bank/inlet/mch/close' || url == '/inter_bank/inlet/mch/close'){
        var msg='<p style="text-align:left;">关闭之后该商户将无法再使用'+title+'</p>';
        _params={mch_id:id,payment_type:payment_type};
    }else if(url == '/bank/inlet/chain/close'　|| url == '/inter_bank/inlet/chain/close'){
        var msg='<p style="text-align:left;">关闭之后旗下的连锁门店将无法再使用'+title+'</p>';
        _params={dt_id:id,payment_type:payment_type};
    }
    var _title='确定关闭'+title+'吗？';
    function getCookie(name) {
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    }
    var xsrf = getCookie("_xsrf");
    $('body').ulaiberLoading({
        loadingTitle:_title,
        loadingText:msg,
        loadingType:'comfirm',
        sureFunction:function(){
            $.ajax({
                headers: {"X-XSRFToken":xsrf},
                type: 'POST',
                data: _params,
                dataType: 'json',
                url: url,
                beforeSend: function () {
                },
                success: function (res) {
                    if(res.code == 200 ){
                        errorTip('关闭成功');
                        setTimeout(function(){
                            openNewTable(id,1);
                        },2000);
                    }else if(res.code == 407){
                        errorTip(res.msg);
                    }else{
                        errorTip('关闭失败请重试');
                    }
                },
                error: function (err) {
                    errorTip('请求失败，请重试')
                }

            });
        }
    });

}

//关闭全部
function rateCloseAll(url,id){
    var _params={};
    if(url == '/bank/inlet/dt/batchClose' || url == '/inter_bank/inlet/dt/batchClose'){
        var msg='<p style="text-align:left;">关闭之后渠道商下的商户将无法再使用全部支付类型</p>';
        _params={dt_id:id};
    }else if(url == '/bank/inlet/mch/batchClose' || url == '/inter_bank/inlet/mch/batchClose'){
        var msg='<p style="text-align:left;">关闭之后该商户将无法再使用全部支付类型</p>';
        _params={mch_id:id};
    }else if(url == '/bank/inlet/chain/batchClose' || url == '/inter_bank/inlet/chain/batchClose'){
        var msg='<p style="text-align:left;">关闭之后旗下的连锁门店将无法再使用全部支付类型</p>';
        _params={dt_id:id};
    }
    function getCookie(name) {
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    }
    var xsrf = getCookie("_xsrf");
    $('body').ulaiberLoading({
        loadingTitle:'确定关闭全部支付类型吗？',
        loadingText:msg,
        loadingType:'comfirm',
        sureFunction:function(){
            $.ajax({
                headers: {"X-XSRFToken":xsrf},
                type: 'POST',
                data: _params,
                dataType: 'json',
                url: url,
                beforeSend: function () {
                },
                success: function (res) {
                    if(res.code == 200 ){
                        errorTip('关闭成功');
                        setTimeout(function(){
                            openNewTable(id,1);
                        },2000);
                    }else if(res.code == 407){
                        errorTip(res.msg);
                    }else{
                        errorTip('关闭失败请重试');
                    }
                },
                error: function (err) {
                    errorTip('请求失败，请重试')
                }

            });
        }
    });

}












