/**
 * Created by apple on 19/5/17.
 */



//获取费率比较值
var payments='{'+$.cookie('rate')+'}';
var paymentsArray=eval('(' + payments + ')');
for(key in paymentsArray){
    if(paymentsArray[key]==0 && has_been_authed == 'True'){
        $('input[name="'+key+'"]').attr('readonly',true)
        $('input[name="'+key+'"]').parents('tr').children().find('input[type="checkbox"]').attr('disabled',true);
    }
}









