/**
 * Created by xiezhigang on 16/11/30.
 */
$().ready(function () {
    var create_at_start = document.getElementById('create_at_start').value;
    var create_at_end = document.getElementById('create_at_end').value;
    var mch_name = document.getElementById('mch_name').value;
    var mch_id = document.getElementById('mch_id').value;

    var payStatusSel = document.getElementById('pay_status');
    var payStatusIndex = payStatusSel.selectedIndex;
    var pay_status = payStatusSel.options[payStatusIndex].value;

    if (document.getElementById('pagination')) {
        var params = "&create_at_start=" + create_at_start + "&create_at_end=" + create_at_end + "&mch_name=" +
            mch_name + "&pay_status=" + pay_status + "&mch_id" + mch_id;

        var href_now = document.getElementById('pagination').getElementsByTagName('a');
        for (var index = 0; index < (href_now.length - 3); index++) {
            v = href_now[index].getAttribute('href');
            if (typeof(v) != 'undefined' || v != null && v && v.match(/\?p=/)) {
                href_now[index].setAttribute('href', v + params);
            }
        }
    }
});