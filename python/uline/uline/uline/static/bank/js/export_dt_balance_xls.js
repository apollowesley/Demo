/**
 * Created by xiezhigang on 16/10/16.
 */

$().ready(function () {
    $("#exportExcel").click(function () {
        var create_at_start = document.getElementById('create_at_start').value;
        var create_at_end = document.getElementById('create_at_end').value;
        var dt_name = document.getElementById('dt_name').value;
        var dt_id = document.getElementById('dt_id').value;
        var channel = document.getElementById('channel').value;

        var payStatusSel = document.getElementById('pay_status');
        var payStatusIndex = payStatusSel.selectedIndex;
        var pay_status = payStatusSel.options[payStatusIndex].value;

        $.ajax({
            type: 'GET',
            data: {
                "create_at_start": create_at_start,
                "create_at_end": create_at_end,
                "dt_name": dt_name,
                "dt_id": dt_id,
                "pay_status": pay_status,
                "total_num": total_num,
                "channel" : channel
            },
            dataType: 'json',
            url: '/bank/balance/dt/export',
            beforeSend: function (XMLHttpRequest) {
            },
            success: function (res) {
                if (res.code == 200) {
                    location.href = res.data
                } else if (res.code == 201) {
                    // alert(res.msg);
                } else if (res.code == 202) {
                    alert(res.msg)
                } else {
                    alert(res.msg)
                }
            },
            complete: function (XMLHttpRequest, textStatus) {
            },
            error: function (xhr) {
            }
        });
        return false;
    })
})
