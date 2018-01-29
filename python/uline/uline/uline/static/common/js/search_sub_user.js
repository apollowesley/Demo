/**
 * Created by apple on 14/4/17.
 */

function formatRepoOne(repo) {
        if (repo.loading) return repo.dt_sub_name;
        markup = "<span>" + repo.dt_sub_name+'('+repo.id+')' + "</span>";
        return markup;
    }

function formatRepoSelectionOne(repo) {
    return   repo.dt_sub_name ;
}
$("#dt_sub_id").siblings('label').css({'font-weight':100});
var allVal=$('#dt_sub_id').attr('all') || '';
$("#dt_sub_id").select2({
    language: 'zh-CN',
    ajax: {
        url: "/dist/sub_user/search?all="+allVal,
        type: "GET",
        dataType: 'json',
        delay: 250,
        data: function (params) {
            return {
                q: params.term,
                page: params.page
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

dt_sub_id = $('#dt_sub_id').val();
// 如果有渠道商子账户，再发送请求获取子账户信息
if (dt_sub_id) {
    $.ajax({
        type : "get",  //提交方式
        url : "/dist/sub_user/info",//路径
        data : {
            "dt_sub_id" : dt_sub_id,
        },//数据，这里使用的是Json格式进行传输
        success : function(result) {//返回数据根据结果进行相应的处理
            if ( result.code ==200 ) {
                console.log(result);
                $('#select2-dt_sub_id-container').text(result.data.dt_sub_name);
            } else {

            }
        }
    });
}









