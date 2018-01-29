/**
 * Created by xiezhigang on 16/11/30.
 */
$().ready(function () {
    var create_at_start = document.getElementById('create_at_start').value;
    var create_at_end = document.getElementById('create_at_end').value;
    var refund_id = document.getElementById('refund_id').value;
    var out_trade_no = document.getElementById('out_trade_no').value;
    var transaction_id = document.getElementById('transaction_id').value;
    var channel = document.getElementById('channel').value;

    var refundStatusSel = document.getElementById('refund_status');
    var refundStatusIndex = refundStatusSel.selectedIndex;
    var refund_status = refundStatusSel.options[refundStatusIndex].value;

    if (document.getElementById('pagination')) {
        var params = "&create_at_start=" + create_at_start + "&create_at_end=" + create_at_end +
            "&refund_id=" + refund_id + "&out_trade_no=" + out_trade_no + "&transaction_id=" + transaction_id +
            "&refund_status=" + refund_status+ "&channel=" + channel;

        var href_now = document.getElementById('pagination').getElementsByTagName('a');
        for (var index = 0; index < (href_now.length - 3); index++) {
            v = href_now[index].getAttribute('href');
            if (typeof(v) != 'undefined' || v != null && v && v.match(/\?p=/)) {
                href_now[index].setAttribute('href', v + params);
            }
        }
    }
});