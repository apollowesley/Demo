/**
 * Created by xiezhigang on 16/10/16.
 */

$().ready(function () {
    $("#exportExcel").click(function () {
        var create_at_start = $("#create_at_start").val();
        var create_at_end = $("#create_at_end").val();
        var dt_id = $(this).attr("name");

        $.ajax({
            type: 'GET',
            data: {"create_at_start": create_at_start, "create_at_end": create_at_end, "dt_id": dt_id},
            dataType: 'json',
            url: '/official/stats/transaction/export/dist',
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