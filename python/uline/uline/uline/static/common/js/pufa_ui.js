/**
 * Created by apple on 12/6/17.
 */

if( env == 'SPD_PROD' || env == 'SPDLOCAL'){
    $('.pad-img').hide();
    $('.pufa-header').show();
    $('.navber-img').css({'display':'block','padding-top':'7px'});
	$('.navber-img>img').attr('src','/static/common/image/pufa_logo.png').css({'padding-right':'10px'});
	$('.navber-img>span').css({'color':'#295386'});
}






