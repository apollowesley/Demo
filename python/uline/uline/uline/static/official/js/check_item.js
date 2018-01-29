/**
 * Created by xiezhigang on 16/11/14.
 */
$('input[type="checkbox"]').change(function () {
    if ($('#checkbox1').is(':checked') == false) {
        $("input[name='checkItem1']").attr('readonly', 'readonly');
    } else {
        $("input[name='checkItem1']").removeAttr('readonly');
    }

    if ($('#checkbox2').is(':checked') == false) {
        $("input[name='checkItem2']").attr('readonly', 'readonly');
    } else {
        $("input[name='checkItem2']").removeAttr('readonly');
    }

    if ($('#checkbox3').is(':checked') == false) {
        $("input[name='checkItem3']").attr('readonly', 'readonly');
    } else {
        $("input[name='checkItem3']").removeAttr('readonly');
    }
});
