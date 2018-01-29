/**
 * Created by base on 13/7/17.
 */


var view  = window.location.pathname;
view=view.split('/')[3];


//http
var DownloadsBillServices={
    'SendDownloadsBill':function(request_data){
        var params=request_data;
        var url='/common/downloads_bill';
        return ajaxResponsePromise(url,params,'POST');
    },
    'SearchName':function(request_data){
        var params=request_data;
        var url='/common/query_mch';
        return ajaxResponsePromise(url,params);
    }
};

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
};


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
    })
}

//解密参数
function getParams() {
    var params = {};
    location.href.replace(/([\w-]+)\=([^\&\=]+)/ig, function (a, b, c) {
        params[b] = c;
    });

    for (var key in params) {
        params[key] = decodeURIComponent(params[key]);
    }
    return params;
}

var params=getParams();


;(function($){

    var _id = {"1":"bank","2":"dist","3":"chain","4":"merchant","5":"official"};
    //click
    $(document).on('click','[data-click]',function(e) {
        e.stopPropagation();
        e.preventDefault();

        var self = $(this),
            name = $(this).data('click');

        switch (name) {

            case 'send':
                if($('[name="id"]').val()==''){
                    $('.error-tip').show().html('请输入名称/编号');
                    return false;
                }else if($('#create_at_start').val()==''){
                    $('.error-tip').show().html('请选择开始时间');
                    return false;
                }else if($('#create_at_end').val()==''){
                    $('.error-tip').show().html('请选择结束时间');
                    return false;
                }
                $('.error-tip').hide();
                DownloadsBillController.SendDownloadsBill();
                return false;
                break;

        }
    });

    var DownloadsBillController={
        SendDownloadsBill:function(){
            var _params={};
            $('form input,form select').each(function(){
                var key=$(this).attr('name');
                _params[key]=$(this).val();
            });
            _params['charac_id']=params.charac_id;
            DownloadsBillServices.SendDownloadsBill(_params).then(function(res){
                if(res.code==200){
                    location.href = res.data;
                }
                else if(res.code==201){
    // errorTipBtn(res.msg);
                window.open(window.location.origin + '/' + _id[params.charac_id] + '/utils/download')
                }
                else{
                    errorTipBtn(res.msg);
                }
            })
        }
    }


})(jQuery);


//模糊查询
function formatRepoOne(repo) {
        if (repo.loading) return repo.name;
        markup = "<span>" + repo.name+'('+repo.id+')' + "</span>";
        return markup;
    }

function formatRepoSelectionOne(repo) {
    return   repo.name ;
}
var getParams=getParams();
$("#search_name").select2({
    language: 'zh-CN',
    ajax: {
        url: "/common/query_mch",
        type: "GET",
        dataType: 'json',
        delay: 250,
        data: function (params) {
            return {
                id_name: params.term,
                page: params.page,
                query_charac:$('[name="query_charac"]').val(),
                charac_id:getParams.charac_id
            };
        },
        processResults: function (data, params) {
            params.page = params.page || 1;
            return {
                results: data.data
            };
        },
        cache: true
    },
    escapeMarkup: function (markup) {
        return markup;
    },
    minimumInputLength: 1,
    templateResult: formatRepoOne,
    templateSelection: formatRepoSelectionOne
});

$('[name="query_charac"]').change(function(){
    if((params.charac_id ==2 && $('[name="query_charac"]').val()==1) || (params.charac_id ==3 && $('[name="query_charac"]').val()==2)){
        $('#search_name').attr('disabled',true);
        $('#search_name').val(id);
        $('#select2-search_name-container').text(id_name);
    }else{
        $('#search_name').removeAttr('disabled');
        $('#search_name').val('');
        $('#select2-search_name-container').text('');
    }

});
if(params.charac_id == parseInt($('[name="query_charac"]').val())+1){
    console.log(id);
    $('#search_name option').val(id);
    $('#select2-search_name-container').text(id_name);
    $('#search_name').attr('disabled',true);
}






