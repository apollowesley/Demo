/**
 * Created by xiezhigang on 16/10/16.
 */

$().ready(function () {
    $("#exportExcel").click(function () {
        var create_at_start = document.getElementById('create_at_start').value;
        var create_at_end = document.getElementById('create_at_end').value;
        var refund_id = document.getElementById('refund_id').value;
        var out_trade_no = document.getElementById('out_trade_no').value;
        var mch_trade_no = document.getElementById('mch_trade_no').value;
        var channel = document.getElementById('channel').value;

        var refundStatusSel = document.getElementById('refund_status');
        var refundStatusIndex = refundStatusSel.selectedIndex;
        var refund_status = refundStatusSel.options[refundStatusIndex].value;

        $.ajax({
            type: 'GET',
            data: {
                "create_at_start": create_at_start,
                "create_at_end": create_at_end,
                "refund_id": refund_id,
                "out_trade_no": out_trade_no,
                "mch_trade_no": mch_trade_no,
                "refund_status": refund_status,
                "channel": channel,
                'total_num': total_num
            },
            dataType: 'json',
            url: '/merchant/transaction/refund/export',
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
