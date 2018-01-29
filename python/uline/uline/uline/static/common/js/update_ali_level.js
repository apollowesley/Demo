/**
 * Created by base on 16/6/17.
 */
function updateAliLevel(mch_id,_this){
    var url='/common/update';
    var _params={
        mch_id:mch_id
    };
    loadingShow();

    $.ajax({
        type: 'GET',
        dataType: 'json',
        data:_params,
        url: url,
        async:false,
        beforeSend: function (XMLHttpRequest) {
        },
        success: function (res) {
            loadingHide();
            if(res.code == 200){
                $('body').ulaiberLoading({
                    loadingTitle:'更新成功',
                    loadingText:'支付宝商户分级信息已更新。',
                    loadingType:'pop'
                })
                _this.prev('em').html(res.data.level);
            }else if(res.code == 407){
                errorTipBtn(res.msg);
            }else{
                $('body').ulaiberLoading({
                    loadingTitle:'更新失败',
                    loadingText:'更新失败，请联系客服人员。',
                    loadingType:'pop'
                })
            }
        },
        complete: function (XMLHttpRequest, textStatus) {
        },
        error: function (xhr) {
            loadingHide();
            errorTip('请求失败，请稍后重试！');
        }

    });
}