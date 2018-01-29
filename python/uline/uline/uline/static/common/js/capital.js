/**
 * Created by liudachu on 25/4/17.
 */


$("#wx_btn").click(function(){
    $("#capital_form").find('input[type="text"],select').val('');
    $('input[name="channel"]').val($(this).attr('data-select'));
    $("#capital_form").submit();
});
$("#ali_btn").click(function(){
    $("#capital_form").find('input[type="text"],select').val('');
    $('input[name="channel"]').val($(this).attr('data-select'));
    $("#capital_form").submit();
});


$('.capital-choose-list li').eq($('input[name="cleared"]').val()).addClass('on');
$('.capital-choose-list li').click(function(){
    if($(this).attr('data-select')!=$('[name="cleared"]').val()){
        $('.form-group input').val('');
        $('input[name="cleared"]').val($(this).attr('data-select'));
        $("#capital_form").submit();
    }
});


