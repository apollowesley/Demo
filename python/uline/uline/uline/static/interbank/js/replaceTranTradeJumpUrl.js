/**
 * Created by xiezhigang on 16/11/30.
 */
$().ready(function () {
    // var create_at_start = document.getElementById('create_at_start').value;
    // var create_at_end = document.getElementById('create_at_end').value;
    var complete_at_start=document.getElementById('complete_at_start').value;
    var complete_at_end=document.getElementById('complete_at_end').value;
    var mch_name = document.getElementById('mch_name').value;
    var dt_name = document.getElementById('dt_name').value;
    var out_trade_no = document.getElementById('out_trade_no').value;
    var channel = document.getElementById('channel').value;

    var tradeStateSel = document.getElementById('trade_state');
    var tradeStateSelIndex = tradeStateSel.selectedIndex;
    var trade_state = tradeStateSel.options[tradeStateSelIndex].value;
    var cs_mch_shortname = document.getElementById('cs_mch_shortname').value;
    var cs_mch_id = document.getElementById('cs_mch_id').value;

    var tradeTypeSel = document.getElementById('trade_type');
    var tradeTypeIndex = tradeTypeSel.selectedIndex;
    var trade_type = tradeTypeSel.options[tradeTypeIndex].value;
    var dt_id = document.getElementById('dt_id').value;
    var mch_id = document.getElementById('mch_id').value;

    if (document.getElementById('pagination')) {
        var params = "&complete_at_start=" + complete_at_start + "&complete_at_end=" + complete_at_end + "&mch_name=" +
            mch_name + "&dt_name=" + dt_name + "&out_trade_no=" + out_trade_no + "&trade_state=" + trade_state +
            "&trade_type=" + trade_type + "&channel=" + channel + "&mch_id=" + mch_id + "&dt_id=" + dt_id +
            "&cs_mch_shortname=" + cs_mch_shortname + "&cs_mch_id=" + cs_mch_id;

        var href_now = document.getElementById('pagination').getElementsByTagName('a');
        for (var index = 0; index < (href_now.length - 3); index++) {
            v = href_now[index].getAttribute('href');
            if (typeof(v) != 'undefined' || v != null && v && v.match(/\?p=/)) {
                href_now[index].setAttribute('href', v + params);
            }
        }
    }
});