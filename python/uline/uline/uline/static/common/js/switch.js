/**
 * Created by liudachu on 27/5/17.
 */
$('.switch').on('click',function(){
    $(this).stop().toggleClass('on');
    if($(this).attr('open-status')==3){
        $(this).attr('open-status','2');
        $(this).children().stop().animate({'left':'22px'});
    }else{
        $(this).attr('open-status','3');
        $(this).children().stop().animate({'left':'2px'});
    }
    open_payment($(this).attr('payment-type'),$(this).attr('open-status'));
});

function switchStatus(){
    $('.switch').each(function(){
        if($(this).attr('open-status')==2){
            $(this).addClass('on');
            $(this).children().css({'left':'22px'});
        }else{
            $(this).removeClass('on');
            $(this).children().css({'left':'2px'});
        }
    });
}
switchStatus();


