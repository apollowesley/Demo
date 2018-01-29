/**
 * Created by base on 21/7/17.
 */
;(function($,window){
    var upload_pic_text = "<i class='base-icon-add' data-click='uploadPic'></i>"
                + "<input class='change-updown' type='file' accept='image/png, image/jpeg' data-change='uploadInput'>"
                + "<img src='' alt='' class='base-upload-img'>",
        picHtml='<div class="base-upload-pic">'+upload_pic_text+'</div>';//上传图片DOM

    var upload_pic_hover="<i class='base-icon-delete glyphicon glyphicon-remove' data-click='deletePic'></i>";//鼠标移动到上传图片效果


    $('.base-upload-img').each(function(){
       if($(this).attr('src') != '' ){
           $(this).after(upload_pic_hover);
       }else{
           $(this).hide();
       }
    });

    $(document).on('click','[data-click]',function(e){

        e.stopPropagation();
        e.preventDefault();

        var self=$(this),
            name=$(this).data('click');

        switch (name){

            case 'uploadPic': //上传图片操作
                self.parents('.base-upload-pic').find('.change-updown').on('change');
                break;

            case 'deletePic': //删除图片操作
                var view=self.parents('.base-upload-box').attr('page-view');
                var params_name=self.parents('.base-upload-box').attr('params-name');
                if(view=='modify'){
                    self.parents('.base-upload-pic').find('img').attr('src','').hide();
                    self.parents('.base-upload-pic').find('input').val('');
                    self.remove();
                }else{
                   var i=0;
                    if($('.base-upload-img').attr('src') != ''){
                        i++;
                    }
                    if(self.parents('.base-upload-box').find('.base-upload-pic').length==5 && $('.base-upload-img').eq(4).attr('src') != ''){
                        self.parents('.base-upload-box').append(picHtml);
                    }
                    self.parents('.base-upload-pic').remove();
                    self.parents('.base-upload-box').find('.base-upload-pic>input').each(function(i){
                        $(this).attr('name',params_name+parseInt(i+1));
                    });
                }
                break;



        }
    });

    $(document).on('change','[data-change]',function(e){

        e.stopPropagation();
        e.preventDefault();

        var self=$(this),
            name=$(this).data('change');


        switch (name){
            case 'uploadInput': //上传图片操作
                var params_name=self.parents('.base-upload-box').attr('params-name');
                var files = e.target.files, file;
                if (files && files.length > 0) {
                    file = files[0];

                    //上传传功,清除掉超过显示
                    $(".imgSize").remove();
                    if (file.size > 1024 * 1024 * 0.5) {
                        errorTip('图片大小不能超过500kb');
                        return false;
                    }
                }
                console.log($('.base-upload-img').eq(4).attr('src'));
                //获取图片的路径，该路径不是图片在本地的路径
                var objUrl = getObjectURL(this.files[0]);
                var img=self.parents('.base-upload-pic').find('.base-upload-img');
                if (objUrl) {
                    //将图片路径存入src中，显示出图片
                    img.show();
                    img.attr("src", objUrl);
                    img.after(upload_pic_hover);
                    if(self.parents('.base-upload-box').find('.base-upload-pic').length<5 && self.attr('class') != 'no-add'){
                        self.parents('.base-upload-box').append(picHtml);
                    }
                    self.parents('.base-upload-box').find('.base-upload-pic>input').each(function(i){
                        $(this).attr('name',params_name+parseInt(i+1));
                    });
                }
                break;



        }
    });


    //建立一個可存取到該file的url
    function getObjectURL(file) {
        var url = null;
        if (window.createObjectURL != undefined) {
            url = window.createObjectURL(file);
        } else if (window.URL != undefined) {
            // 火狐
            url = window.URL.createObjectURL(file);
        } else if (window.webkitURL != undefined) {
            // 谷歌
            url = window.webkitURL.createObjectURL(file);
        }
        return url;
    }

})(jQuery,window);


