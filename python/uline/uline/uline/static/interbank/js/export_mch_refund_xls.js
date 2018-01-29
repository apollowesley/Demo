/**
 * Created by xiezhigang on 16/10/16.
 */

$().ready(function () {
    $("#exportExcel").click(function () {
        var create_at_start = document.getElementById('create_at_start').value;
        var create_at_end = document.getElementById('create_at_end').value;
        var mch_name = document.getElementById('mch_name').value;
        var dt_name = document.getElementById('dt_name').value;
        var refund_id = document.getElementById('refund_id').value;
        var out_trade_no = document.getElementById('out_trade_no').value;
        var transaction_id = document.getElementById('transaction_id').value;
        var channel = document.getElementById('channel').value;
         var cs_mch_shortname = document.getElementById('cs_mch_shortname').value;
        var cs_mch_id = document.getElementById('cs_mch_id').value;

        var refundStatusSel = document.getElementById('refund_status');
        var refundStatusIndex = refundStatusSel.selectedIndex;
        var refund_status = refundStatusSel.options[refundStatusIndex].value;

        $.ajax({
          type: 'GET',
          data: {
              "create_at_start":create_at_start,
              "create_at_end":create_at_end,
              "mch_name": mch_name,
              "dt_name": dt_name,
              "refund_id": refund_id,
              "out_trade_no": out_trade_no,
              "transaction_id": transaction_id,
              "refund_status": refund_status,
              "channel": channel,
              "total_num": total_num,
               "cs_mch_shortname": cs_mch_shortname,
                "cs_mch_id": cs_mch_id

          },
          dataType: 'json',
          url: '/inter_bank/transaction/refund/export',
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
