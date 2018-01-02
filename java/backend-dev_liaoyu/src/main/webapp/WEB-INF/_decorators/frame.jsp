<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>

<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
     <title><decorator:title default="后台管理系统" /></title>
     
     <link rel="stylesheet" type="text/css" href="${_path}/css/admin_style.css"></link>
     <script type="text/javascript" src="${_path}/js/jquery-1.8.3.min.js"></script>
     <script type="text/javascript" src="${_path}/js/develop.js"></script>
     <script type="text/javascript" src="${_path}/js/showmsg.js"></script>
     <script type="text/javascript" src="${_path}/js/jquery.validate-1.13.1.min.js"></script>
     
     <script> 
		var isCommitted = false; 
		function checkPost() 
		{ 
			//if(!isCommitted) 
			//{ 
			//	isCommitted = true; 
				return true; 
			//} 
			//else 
			//{ 
			//	return false; 
			//} 
		} 
		
		</script> 

     <decorator:head />
  </head>
  <body class="right_body">
     <decorator:body />
  </body>
</html>