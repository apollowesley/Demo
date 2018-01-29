

 $().ready(function(){
    //添加三角箭头
    var tabs = document.getElementById('tabs');
    var oLi  = tabs.getElementsByTagName('li');
    for(i=0,len=oLi.length; i<len; i++){
        oLi[i].onclick = function(){
            //清除当前active
            this.classList.remove("active");
            //添加clas是名
            this.classList.add("active","col-md-2");
            //清除三角形
            $('.triangles').remove();
            //添加border
            $('.col-md-2').css("border","1px solid #ccc");
            if(this.classList.contains("active")){
                var result  = '<div class="triangles">'+
                                    '<div class="triangle-down"></div>'+
                              '</div>'
                //添加内容
                $(this).append(result);
                //去除border
                $(this).css("border","0px");
            }
        }
    }
})
