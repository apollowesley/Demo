/**
 * Created by liudachu on 15/5/17.
 * 导出接口公用请求方法
 */
function exportXls(file_type){
    var _params='',url='';
    var _str=window.location.pathname;
    var _path=_str.split('/');

    loadingShow();

    $('.export-xls input,.export-xls .form-group select').each(function(){
        var _value='';
        if(!$(this).attr('disabled')){
            if($(this).val() == null){
                _value=''
            }else{
                _value=$(this).val()
            }
            _params+='&'+$(this).attr('name')+'='+_value;
        }
    });

    if(file_type != undefined){
        $('#exportChoose').modal('hide');
        _params+='&file_type='+file_type;
    }

    _params="total_num="+total_num+_params;
    url=_str+'/export?'+_params;

    /*if(total_num >= 1000){
        $('.open-down').remove();
        setTimeout(function(){
            loadingHide();
            window.open('/'+_path[1]+'/utils/download');
        },3000);
    }*/


    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        beforeSend: function (XMLHttpRequest) {
        },
        success: function (res) {
            loadingHide();
            if (res.code == 200) {
                location.href = res.data;
            } else if (res.code == 201) {
                window.open('/'+_path[1]+'/utils/download');
            } else if (res.code == 202) {
                errorTipBtn(res.msg);
            } else {
                errorTipBtn(res.msg);
            }
        },
        complete: function (XMLHttpRequest, status) {
        },
        error: function (xhr) {
            loadingHide();
        }

    });
}
$("#exportExcel").on('click',function () {
    exportXls();
    return false;
});






















