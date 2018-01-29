/**
 * Created by xiezhigang on 16/10/16.
 */

$().ready(function () {
    $("#exportExcel").click(function () {
        var create_at_start = document.getElementById('create_at_start').value;
        var create_at_end = document.getElementById('create_at_end').value;
        var mch_trade_no = document.getElementById('mch_trade_no').value;
        var channel = document.getElementById('channel').value;

        var tradeStateSel = document.getElementById('trade_state');
        var tradeStateSelIndex = tradeStateSel.selectedIndex;
        var trade_state = tradeStateSel.options[tradeStateSelIndex].value;

        var tradeTypeSel = document.getElementById('trade_type');
        var tradeTypeIndex = tradeTypeSel.selectedIndex;
        var trade_type = tradeTypeSel.options[tradeTypeIndex].value;

        $.ajax({
            type: 'GET',
            data: {
                "create_at_start": create_at_start,
                "create_at_end": create_at_end,
                "mch_trade_no": mch_trade_no,
                "trade_state": trade_state,
                "trade_type": trade_type,
                "channel": channel,
                'total_num': total_num
            },
            dataType: 'json',
            url: '/merchant/transaction/trade/export',
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
