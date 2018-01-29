/**
 * Created by xiezhigang on 16/11/30.
 */
$().ready(function () {
    var create_at_start = document.getElementById('create_at_start').value;
    var create_at_end = document.getElementById('create_at_end').value;
    var out_refund_no = document.getElementById('out_refund_no').value;

    var handleStatusSel = document.getElementById('handle_status');
    var handleStatusIndex = handleStatusSel.selectedIndex;
    var handle_status = handleStatusSel.options[handleStatusIndex].value;

    var exceptTypeSel = document.getElementById('except_type');
    var exceptTypeIndex = exceptTypeSel.selectedIndex;
    var except_type = exceptTypeSel.options[exceptTypeIndex].value;

    if (document.getElementById('pagination')) {
        var params = "&create_at_start=" + create_at_start + "&create_at_end=" + create_at_end + "&out_refund_no=" +
            out_refund_no + "&handle_status=" + handle_status + "&except_type=" + except_type;

        var href_now = document.getElementById('pagination').getElementsByTagName('a');
        for (var index = 0; index < (href_now.length - 3); index++) {
            v = href_now[index].getAttribute('href');
            if (typeof(v) != 'undefined' || v != null && v && v.match(/\?p=/)) {
                href_now[index].setAttribute('href', v + params);
            }
        }
    }
});