/**
 * Created by xiezhigang on 16/10/16.
 */

$().ready(function () {
    $("#exportExcel").click(function () {
        var create_at_start = document.getElementById('create_at_start').value;
        var create_at_end = document.getElementById('create_at_end').value;
        var out_trade_no = document.getElementById('out_trade_no').value;

        var handleStatusSel = document.getElementById('handle_status');
        var handleStatusIndex = handleStatusSel.selectedIndex;
        var handle_status = handleStatusSel.options[handleStatusIndex].value;

        var exceptTypeSel = document.getElementById('except_type');
        var exceptTypeIndex = exceptTypeSel.selectedIndex;
        var except_type = exceptTypeSel.options[exceptTypeIndex].value;

        $.ajax({
          type: 'GET',
          data: {"create_at_start":create_at_start, "create_at_end":create_at_end,
              "out_trade_no": out_trade_no, "handle_status": handle_status, 'except_type': except_type,
              "total_num": total_num},
          dataType: 'json',
          url: '/inter_bank/recon/transaction/export',
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
