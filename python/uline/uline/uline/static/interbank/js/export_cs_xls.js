/**
 * Created by xiezhigang on 16/10/16.
 */

$().ready(function () {
    $("#exportExcel").click(function () {
        var create_at_start = document.getElementById('create_at_start').value;
        var create_at_end = document.getElementById('create_at_end').value;
        var short_name = document.getElementById('short_name').value;
        var cs_name = document.getElementById('cs_name').value;
        var cs_id = document.getElementById('cs_id').value;
        var mch_id = document.getElementById('mch_id').value;

        var activatedStatusSel = document.getElementById('activated_status');
        var activatedStatusIndex = activatedStatusSel.selectedIndex;
        var activated_status = activatedStatusSel.options[activatedStatusIndex].value;

        var authStatusSel = document.getElementById('auth_status');
        var authStatusIndex = authStatusSel.selectedIndex;
        var auth_status = authStatusSel.options[authStatusIndex].value;

        $.ajax({
            type: 'GET',
            data: {
                "create_at_start": create_at_start,
                "create_at_end": create_at_end,
                "short_name": short_name,
                "cs_name": cs_name,
                "cs_id": cs_id,
                "mch_id": mch_id,
                'activated_status': activated_status,
                'auth_status': auth_status,
                'total_num': total_num
            },
            dataType: 'json',
            url: '/inter_bank/inlet/cs/export',
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
