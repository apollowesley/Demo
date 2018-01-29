/**
 * Created by apple on 12/5/17.
 */
if(navigator.appName == "Microsoft Internet Explorer"&&parseInt(navigator.appVersion.split(";")[1].replace(/[ ]/g, "").replace("MSIE",""))<8){
    window.location.href='/common/browser';
}//判断浏览器版本过低操作

$(function(){
   if( env == 'SPD_PROD' || env == 'SPDLOCAL'){
        $('.logo>img').attr('src','/static/common/image/pufa_login_logo.png');
        $('.emailImg').eq(0).attr('src','/static/common/image/pufa_user.png');
        $('.emailImg').eq(1).attr('src','/static/common/image/pufa_password.png');
        $('button[type="submit"]').css({'background':'#043671','border-color':'#043671'});
    }
});










