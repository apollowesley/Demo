
$().ready(function(){
	//-------------点击tr变色--------------
	$('table tbody tr').click(function(){
		$(this).addClass("hover").siblings().removeClass("hover");
	});
	$('.table-no-click tbody tr').unbind('click');
});


if( env == 'SPD_PROD' || env == 'SPDLOCAL'){
	$('.navber-img').css({'display':'block','padding-top':'7px'});
	$('.navber-img>img').attr('src','/static/common/image/pufa_logo.png').css({'padding-right':'10px'});
	$('.navber-img>span').css({'color':'#295386'});
}


//城市三级联动
if($('.distpicker').length>0){
	$('.distpicker').distpicker();
}



//设置费率cookie
function setRateCookie(options){
    var options=options.substring(0,options.length-1);
    $.cookie('rate',options);
}
