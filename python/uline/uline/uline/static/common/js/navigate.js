$(document).ready(function () {

    $("#id_jump_to").unbind("click").click(function (e) {

        e.preventDefault();
        var jump_to = $('#input_v').val();
        max_page = page_number;
        var jump_to_no = Number(jump_to);

        if (jump_to.length > 0 && !$.isNumeric(jump_to) || jump_to_no > max_page || jump_to_no <= 0) {
            alert('请输入有效数字!');
            $('input[name=jump]').val('');
            return false;
        } else {
            var href_now = $('.pagination a[href]').attr('href');
            href_jump = href_now.replace(/p=\d+/, 'p=' + jump_to);
            location.href = href_jump;
        }
    })
});