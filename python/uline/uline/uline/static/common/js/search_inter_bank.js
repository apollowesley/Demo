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
$("#bk_id").siblings('label').css({'font-weight':100});
var allVal=$('#bk_id').attr('all') || '';
$("#bk_id").select2({
    language: 'zh-CN',
    ajax: {
        url: "official/inlet/bank/profile "+allVal,
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









