/**
 * Created by apple on 16/5/17.
 */

$('.tab-nav li').click(function(){
    var index = $(this).index();
    $('input[name="query_date"]').val(index+1);
    $('.export-xls').find('input[type="text"]').val('');
    $('.form_datetime').eq(index).removeAttr('disabled');
    $('.form_datetime').eq(index).siblings('.form_datetime').attr('disabled',true);
    $('.form_datetime').eq(index).show().siblings('.form_datetime').hide();
    $('.tab_container').eq(index).show().siblings('.tab_container').hide();
    $(this).addClass('on').siblings().removeClass('on');
    $(".export-xls").submit();
});

$('.tab-nav li').each(function(index){
	if($(this).hasClass('on')){
	    $('input[name="query_date"]').val(index+1);
		$('.form_datetime').eq(index).removeAttr('disabled');
        $('.form_datetime').eq(index).siblings('.form_datetime').attr('disabled',true);
        $('.form_datetime').eq(index).show().siblings('.form_datetime').hide();
        $('.tab_container').eq(index).show().siblings('.tab_container').hide();
	}
})



$('.select-time li').click(function(){
    var index = $(this).index();
    $('input[name="query_date"]').val(index+1);
    $('.form-inline').find('input[type="text"]').val('');
    $('.statInput').eq(index).find('input').removeAttr('disabled');
    $('.statInput').eq(index).siblings('.statInput').find('input').attr('disabled',true);
    $('.statInput').eq(index).show().siblings('.statInput').hide();
    $(this).addClass('on').siblings().removeClass('on');
    $(".export-xls").submit();
});

$(function(){
   $('.select-time li').each(function(index){
        if($(this).hasClass('on')){
            $('input[name="query_date"]').val(index+1);
            $('.statInput').eq(index).find('input').removeAttr('disabled');
            $('.statInput').eq(index).siblings('.statInput').find('input').attr('disabled',true);
            $('.statInput').eq(index).show().siblings('.statInput').hide();
        }
    })
});






