/**
 * Created by xiezhigang on 16/11/14.
 */
$().ready(function () {
    function formatRepo(repo) {
        if (repo.loading) return repo.text;
        markup = "<option value='" + repo.id + "'>" + repo.bank_name + "</option>";
        return markup;
    }

    function formatRepoSelection(repo) {
        return repo.bank_name || repo.text || repo.id
    }

    $("#bankNo").select2({
        language: 'zh-CN',
        ajax: {
            url: "/official/inlet/dt/bank",
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
});