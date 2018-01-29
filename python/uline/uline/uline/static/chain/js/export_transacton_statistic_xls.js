/**
 * Created by xiezhigang on 16/10/16.
 */

$().ready(function () {
    $("#exportExcelOne").click(function () {
        var create_at_start = $("#create_at_start").val();
        var create_at_end = $("#create_at_end").val();

        $.ajax({
            type: 'GET',
            data: {"create_at_start":create_at_start, "create_at_end":create_at_end},
            dataType: 'json',
            url: '/chain/stats/transaction/export',
            beforeSend: function (XMLHttpRequest) {},
            success: function (res) {
                if (res.code == 200){
                    location.href = res.data
                } else {
                    alert(res.msg)
                }
            },
            complete: function (XMLHttpRequest, textStatus) {},
            error: function (xhr) {
                console.log("Error: " + xhr.statusText);
                alert('服务器繁忙')
            }
        });
        return false;
    })
});
