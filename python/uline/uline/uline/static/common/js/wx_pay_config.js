/**
 * Created by base on 20/6/17.
 */
var wx_url=window.location.pathname+'/wx_config';
//获取微信配置：
function getWxPayConfig(mch_id,operation,updateStatus,refresh){
    var _params={
        mch_id:mch_id,
        refresh:refresh?refresh:'1'
    };
    if(updateStatus){
        loadingShow();
    }

    var appendAddressHtml='';

    $.ajax({
        type: 'GET',
        dataType: 'json',
        data:_params,
        url: wx_url,
        beforeSend: function (XMLHttpRequest) {
        },
        success: function (res) {
            if(updateStatus){
                loadingHide();
                errorTip('更新成功');
            }
            var wxPayData=res.wx_configs;

            for(var i=0;i<wxPayData.length;i++){
                //微信支付配置--千二
                appendAddressHtml += '<div class="base-wx-box">';
                appendAddressHtml += '<h4>微信支付配置（'+wxPayData[i].channel_name+'）<span class="m-left-5 base-error-c">'+wxPayData[i].wx_msg+'</span>';
                /*if(!operation){*/
                    appendAddressHtml += '<a href="javascript:;" onclick="updateWxConfig('+mch_id+')" class="m-left-5">更新</a>';
                /*}*/
                appendAddressHtml += '</h4>';
                var default_subscribe=1;
                if (wxPayData[i].default_subscribe == '') {
                    wxPayData[i].default_subscribe = '未设置';
                    default_subscribe=0;
                }
                appendAddressHtml += '<p>推荐关注公众号：' + wxPayData[i].default_subscribe + '';
                if(operation){
                    appendAddressHtml+='<a href="javascript:;" class="m-left-5" onclick="updateJsApi('+default_subscribe+',1,'+wxPayData[i].channel_type+')">修改</a>'
                }
                appendAddressHtml+='</p>'
                appendAddressHtml += '<p>公众号支付授权目录（支付相关域名）';
                if(operation){
                    appendAddressHtml+='<a href="javascript:;" class="m-left-5" onclick="updateJsApi('+wxPayData[i].jsapi_path_list.length+',2,'+wxPayData[i].channel_type+')">修改</a>';
                }
                appendAddressHtml+='</p>';
                if (wxPayData[i].jsapi_path_list.length > 0) {
                    var wxUpdateJsMsg=''
                    appendAddressHtml += '<table>';
                    appendAddressHtml += '<tbody>';
                    appendAddressHtml += '<tr>';
                    appendAddressHtml += '<th rowspan="' + wxPayData[i].jsapi_path_list.length + '" class="base-table-bg">JS API支付授权目录</th>';

                    appendAddressHtml += '<td>' + wxPayData[i].jsapi_path_list[0] + '</td>';
                    appendAddressHtml += '</tr>';
                    for (var j = 1; j < wxPayData[i].jsapi_path_list.length; j++) {
                        appendAddressHtml += '<tr>';
                        appendAddressHtml += '<td>'+wxPayData[i].jsapi_path_list[j]+'</td>';
                        appendAddressHtml += '</tr>';
                    }
                    appendAddressHtml += '</tbody>';
                    appendAddressHtml += '</table>';
                }
                appendAddressHtml += '<p>微信APPID';
                if(operation){
                    appendAddressHtml+='<a href="javascript:;" class="m-left-5" onclick="addWxAppid('+wxPayData[i].channel_type+')">添加</a>';
                }
                appendAddressHtml += '</p><table>';
                appendAddressHtml += '<thead>';
                appendAddressHtml += '<tr><th>序号</th><th>APPID</th>';
                if(operation){
                    appendAddressHtml+='<th>操作</th>';
                }
                appendAddressHtml += '</tr></thead>';
                appendAddressHtml += '<tbody>';
                if (wxPayData[i].appid_config_list.length > 0) {
                    for (var j = 0; j < wxPayData[i].appid_config_list.length; j++) {
                        appendAddressHtml += '<tr>';
                        appendAddressHtml += '<td>' + (j+1) + '</td><td>' + wxPayData[i].appid_config_list[j].sub_appid + '</td>';
                        if(operation){
                            appendAddressHtml+='<td><a href="javascript:;" onclick=deleteAppid();>删除</a></td>';
                        }
                        appendAddressHtml += '</tr>';
                    }
                } else {
                    appendAddressHtml += '<tr>';
                    appendAddressHtml += '<td colspan="3" style="text-align: center !important;">暂无数据</td>';
                    appendAddressHtml += '</tr>';
                }
                appendAddressHtml += '</tbody>';
                appendAddressHtml += '</table>';
                appendAddressHtml += '</div>';
            }


            if(wxPayData.length==0){
                $('.wx-config-wrap').html('<p style="padding:50px;font-size:16px;color:#999;text-align: center;">商户未开通微信支付</p>');
            }else{
                $('.wx-config-wrap').html(appendAddressHtml);
            }
        },
        complete: function (XMLHttpRequest, textStatus) {
        },
        error: function (xhr) {
            appendAddressHtml='';
        }
    });
    //return appendAddressHtml;
}

function updateWxConfig(mch_id){
    var url=window.location.pathname;
    url=url.split('/')[1];
    if(url == 'dist'){
        var _html=getWxPayConfig(mch_id,true,true,2);
    }else{
        var _html=getWxPayConfig(mch_id,false,true,2);
    }
    $('.wx-config-wrap').html(_html);
}


//微信配置：
function setWxConfig(config_key,_this){
    if(config_key == 'jsapi_path'){
        var str=$('.base-http').val();
        if(str == ''){
            errorTip('输入不能为空');
            return false;
        }else if(str.charAt(str.length - 1) != '/') {
            errorTip('必须以左斜杠“/”结尾');
            return false;
        }
        var config_value=[];
        config_value.push(str);
        config_value=JSON.stringify(config_value);
    }else{
        var str=_this.parents('.modal-content').find('input[name="config_value"]').val();
        if(str == ''){
            errorTip('输入不能为空');
            return false;
        }
        var config_value=str;
    }
    var thisId=_this.parents('.base-modal').attr('id');
    $('#'+thisId).modal('hide');
    loadingShow();
    var _params={
            "mch_id":$('#thisMchId').val(),
            "config_key":config_key ,//'subscribe_appid', 'sub_appid','jsapi_path'取其一
            "config_value":config_value,//配置的值,支付目录时为list,'subscribe_appid', 'sub_appid'时，为string,
            "config_type":$('#'+thisId).attr('data-channel-type'),
            "_xsrf":$('input[name="_xsrf"]').val()
        };

    $.ajax({
        type: 'POST',
        dataType: 'json',
        data:_params,
        url: wx_url,
        beforeSend: function (XMLHttpRequest) {
        },
        success: function (res) {
            loadingHide();
            if(res.code==200){
                errorTip(res.msg);
                var _html=getWxPayConfig(_params.mch_id,true);
                $('.wx-config-wrap').html(_html);
            }else{
                errorTipBtn(res.msg);
            }
        },
        complete: function (XMLHttpRequest, textStatus) {
        },
        error: function (xhr) {
            loadingHide();
            errorTip('请求失败，请重试！');
        }

    });
}


function updateJsApi(len,type,channel_type){
    if(type == 2 && len<5){
        $('#updateJsApi').modal('show');
        $('#updateJsApi').attr('data-channel-type',channel_type);
        $('.base-api-list').html('');
        $('.base-input-select input').val('');
    }else if(len>0){
        errorTipBtn('微信支付没有提供修改接口，请联系客服人员协助修改相关参数，客服电话 <br>400-804-7555');
    }else{
        $('#attentionWx').modal('show');
        $('#attentionWx').attr('data-channel-type',channel_type);
    }
}
function addWxAppid(channel_type){
    $('input[name="config_value"]').val('');
    $('#addAppid').modal('show');
    $('#addAppid').attr('data-channel-type',channel_type);
}
function deleteAppid(){
    errorTipBtn('微信支付没有提供删除接口，请联系客服人员协助修改相关参数，客服电话<br> 400-804-7555');
}


//公众号支付配置添加删除操作
$('.add-jsapi').click(function(){
    var str=$(this).siblings('input').val();
    if(str.indexOf('http') != 0 ){
        str=$(this).siblings('select').val()+str;
    }
    console.log(str);
    if(str.charAt(str.length - 1) != '/'){
        errorTip('必须以左斜杠“/”结尾');
    }else if(str != ''){
        var _html='<p><span>'+str+'</span><a href="javascript:;" onclick="deleteJsApi($(this))">删除</a></p>';
        $('.base-api-list').append(_html);
    }else{
        errorTip('输入不能为空');
    }
});
function deleteJsApi(_this){
    _this.parents('p').remove();
}



function ValidateValue(textbox) {
    var IllegalString = ",#&￥$%[]\"{}'<>;`";
    var textboxvalue = textbox.val();
    var index = textboxvalue.length - 1;

    var s = textbox.val().charAt(index);

    if (IllegalString.indexOf(s) >= 0) {
        s = textboxvalue.substring(0, index);
        textbox.val(s);
    }

}
