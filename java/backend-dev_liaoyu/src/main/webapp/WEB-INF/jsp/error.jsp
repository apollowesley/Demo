<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/_decorators/base.jsp" %>

<html> 
	<head><title>出错啦！！！</title></head> 
	<body class="right_body">
	  <div class="body">
			<div class="top_subnav"> 出错啦！！！<a href="javascript:history.go(-1)">返回</a></div>
			 <div  style="display:none;">
				${ex}
			 </div>
	  </div>
	</body>
</html>
