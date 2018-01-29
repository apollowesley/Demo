/**
 * Created by xiezhigang on 16/11/30.
 */
$().ready(function () {
    var create_at_start = document.getElementById('create_at_start').value;
    var create_at_end = document.getElementById('create_at_end').value;
    var mch_name = document.getElementById('mch_name').value;
    var mch_id = document.getElementById('mch_id').value;
    var dt_sub_id = document.getElementById('dt_sub_id').value;

    var activatedStatusSel = document.getElementById('activated_status');
    var activatedStatusIndex = activatedStatusSel.selectedIndex;
    var activated_status = activatedStatusSel.options[activatedStatusIndex].value;

    var authStatusSel = document.getElementById('auth_status');
    var authStatusIndex = authStatusSel.selectedIndex;
    var auth_status = authStatusSel.options[authStatusIndex].value;

    if (document.getElementById('pagination')) {
        var params = "&create_at_start=" + create_at_start + "&create_at_end=" + create_at_end + "&mch_name=" +
            mch_name + "&activated_status=" + activated_status + "&auth_status=" + auth_status + "&mch_id=" + mch_id +
                "&dt_sub_id=" + dt_sub_id;

        var href_now = document.getElementById('pagination').getElementsByTagName('a');
        for (var index = 0; index < (href_now.length - 3); index++) {
            v = href_now[index].getAttribute('href');
            if (typeof(v) != 'undefined' || v != null && v && v.match(/\?p=/)) {
                href_now[index].setAttribute('href', v + params);
            }
        }
    }
});