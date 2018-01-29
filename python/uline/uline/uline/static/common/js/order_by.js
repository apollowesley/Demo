/**
 * Created by apple on 17/5/17.
 */
$('.order-by').click(function(){
    $('input[name="order_by"]').val($(this).attr('name'));
    $('form').submit();
});

$('.table th').each(function(index){
    if($(this).attr('name') == $('input[name="order_by"]').val()){
        $(this).css({color:'#428bca'});
    }
});