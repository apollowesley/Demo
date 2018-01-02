<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/_decorators/base.jsp"%>
<page:apply-decorator name="frame">
<html>
<head><title>图片管理</title></head>
<body class="right_body">
	<div class="body">
		<div class="top_subnav">${sessionScope.breadcrumb}</div>
        <div class="tablelist">
		  <div class="navtop">替换图片</div>
		  <form action="update" method="post" enctype="multipart/form-data" id="formid">
		  <input type="hidden" id="token_" name="token_" value="${sessionScope.token_}" />
           <div class="addpage_con">
           	 <input type="hidden" name="imgId" id="imgId" value="${picture.id }"/>
           	 <input type="hidden" name="tag" id="tag" value="${picture.tag }"/>
           	 <input type="hidden" name="dateStr" id="dateStr" value="${picture.dateStr }"/>
           	 <input type="hidden" name="folder" id="folder" value="${picture.folder }"/>
           	 <input type="hidden" name="description" id="description" value="${picture.description }"/>
             <ul><li class="biaoming">缩略图</li><li class="addbiao"><img src='${picture.pictureUrl}' class='img'  width="238" height="238" /></li></ul>
             <ul><li class="biaoming">上传<font color="red"> *</font></li><li class="addbiao"><input name="image" type="file" id="input" value="添加图片" /></li></ul>
             <ul><li class="biaoming">&nbsp;</li><li class="addbiao">
             <button type="reset" onclick="javascript:history.go(-1)">返回</button>
             <button type="button">提交</button></li></ul>
              <div id="errorMsg" style="color: red"></div>
            </div>
            <div class="showMsg" id="msgbox" style="text-align:center;display:none;">
				<h5>提示信息</h5>
			    <div class="content guery" style="display:inline-block;display:-moz-inline-stack;zoom:1;*display:inline; max-width:350px">
                                     	请先选择一张图片
                </div>
			    <div class="bottom">
			    	<a href="javascript:closemsg()" >我知道啦</a>
			    </div>
			</div>
			
          </form>  
        </div>
	</div>
</body>

</html>
</page:apply-decorator>
<script type="text/javascript" src="${_path}/js/imageUpload.js"></script>
<script type="text/javascript">
//注册按钮提交事件
$(function() {
	   $("button[type^='button']").click(function() {
		   var file = $('#input').val();
		   if(file.length<=0){
			 showmsg();
			 return false;
		   }
		   if(checkPost())
		   {
			  $('#formid').submit();
		   }
	   });
});
</script>