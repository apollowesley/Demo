/**
 * Created by xiezhigang on 16/10/16.
 */

$().ready(function () {
    $("#exportExcel").click(function () {
        var create_at_start = $("#create_at_start").val();
        var create_at_end = $("#create_at_end").val();
        var create_at_start_moon = $("#create_at_start_moon").val();
        var create_at_end_moon = $("#create_at_end_moon").val();

        $.ajax({
            type: 'GET',
            data: {"create_at_start": create_at_start, "create_at_end": create_at_end},
            dataType: 'json',
            url: '/inter_bank/stats/transaction/export',
            beforeSend: function (XMLHttpRequest) {
            },
            success: function (res) {
                if (res.code == 200) {
                    location.href = res.data
                } else {
                    alert(res.msg)
                }
            },
            complete: function (XMLHttpRequest, textStatus) {
            },
            error: function (xhr) {
                alert('操作频繁，请稍后刷新页面重试')
            }
        });
        return false;
    })
});