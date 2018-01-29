
;(function($){
    $.ajax({
        type:'GET',
        url:'/common/have_permission',
        data:'',
        dataType:'json',
    }).then(function(res){
        console.log(res);
        var navList=res.data.permission;
        for(var i=0;i<navList.length;i++){
            if(res.data.cs_name){
                $('#side-menu [href*="'+navList[i].model_url+'"]').html(navList[i].model_name);
            }
            $('[href*="'+navList[i].model_url+'"]').parents('li').show();
            $('[href*="'+navList[i].model_url+'"]').parent('div').parent('div').show();
        }
    })
})(jQuery);
