<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/_decorators/base.jsp" %>

<html> 
	<head>
	   <title>登陆</title>
	</head> 
	<body> 
	   <form id="loginFrom" action="${_path}/home/login" method="post" autocomplete="off">
           <div class="login">
			  <div class="login_form">
			    <div class="form_info">
			      <div class="field">
			        <label>用户名：</label>
			        <input id="username" name="username" value="${username}" type="text" class="text" size="20" autocomplete="off">
			      </div>
			      <div class="field">
			        <label>密　码：</label>
			        <input id="password" name="password" value="" type="password" class="text" size="20" autocomplete="off">
			      </div>
			      <div class="field">
			        <label>验证码：</label>
			        <input id="vecode" name="vecode" value="" type="text" class="text" size="10">
			        <cite class="yzm"><img title="看不清? 可单击图片刷新" src="${_path}/home/randnumberimage" onclick="this.src='${_path}/home/randnumberimage?d='+Math.random();"/></cite>
			      </div>
			      <div class="field">
			        <label></label>
			       <!--  <button class="button" style="margin-left:50px;_margin-left:48px"></button> -->
			        <input type="submit" value="登陆">
			      </div>
			      <div id="error" class="error">${error}</div>
			    </div>
			  </div>
			</div>
			
		</form>
	</body>
</html>

