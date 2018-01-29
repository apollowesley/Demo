/**
 * Created by lx on 17/3/23.
 */
$(document).ready(function(){
    var selectUtil = new SelectUtil('chain_id');
    selectUtil.bind_select('chainSelect', '/chain/inlet/cs/chain_info');
});


function SelectUtil(hidden_id){

    var formatRepo = function(repo) {
        if (repo.loading) return repo.text;
        markup = "<option value='" + repo.id + "'>" + repo.bank_name + "</option>";
        return markup;
    };

    var formatRepoSelection = function(repo) {
        if (hidden_id != null){
            $("#" + hidden_id).val(repo.id);
        }
        return repo.bank_name
    };
    /**
     * select2通用绑定方法 --> 进件时结算银行那里所使用的控件
     * @param id 控件的ID
     * @param get_url 获取数据请求的URL
     */
    this.bind_select = function(id, get_url){
        $("#" + id).select2({
            language: 'zh-CN',
            ajax: {
                url: get_url,
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
                        results: data.data,
                        pagination: {
                            more: (params.page * 10) < data.total_count
                        }
                    };
                },
                cache: true
            },
            escapeMarkup: function (markup) {
                return markup;
            },
            minimumInputLength: 1,
            templateResult: formatRepo,
            templateSelection: formatRepoSelection
        });
    }
}