/**
 * Created by lifeng on 2017/4/13.
 */
$().ready(function () {
    var create_at_start = document.getElementById('create_at_start').value;
    var create_at_end = document.getElementById('create_at_end').value;
    var mch_sub_name = document.getElementById('mch_sub_name').value;

    var statusSel = document.getElementById('mch_sub_status');
    var statusIndex = statusSel.selectedIndex;
    var status = statusSel.options[statusIndex].value;

    if (document.getElementById('pagination')) {
        var params = "&create_at_start=" + create_at_start + "&create_at_end=" + create_at_end +
            "&mch_sub_name=" + mch_sub_name + '&status=' + status;
        var href_now = document.getElementById('pagination').getElementsByTagName('a');
        for (var index = 0; index < (href_now.length - 3); index++) {
            v = href_now[index].getAttribute('href');
            if (typeof(v) != 'undefined' || v != null && v && v.match(/\?p=/)) {
                href_now[index].setAttribute('href', v + params);
            }
        }
    }
});
