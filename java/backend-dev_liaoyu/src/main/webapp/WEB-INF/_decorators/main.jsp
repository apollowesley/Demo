<%@page import="com.kyl.ps.model.config.CustomMenuChild"%>
<%@page import="com.kyl.ps.model.config.CustomMenu"%>
<%@page import="com.kyl.ps.model.config.ModuleMenu"%>
<%@page import="java.util.List"%>
<%@page import="com.kyl.ps.jee.JEEConstant"%>
<%@page import="com.kyl.ps.model.manageruser.ManagerUser"%>
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/_decorators/base.jsp" %>

<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
     <title><decorator:title default="嗨拍后台管理系统 :: 成都科意隆" /></title>
     
     <link rel="stylesheet" type="text/css" href="${_path}/css/admin_style.css"></link>
     <link rel="stylesheet" type="text/css" href="${_path}/css/skins/tpphp.css"></link>
     <script type="text/javascript" src="${_path}/js/jquery-1.8.3.min.js"></script>
     <script type="text/javascript" src="${_path}/js/main.js"></script>
     <script type="text/javascript" src="${_path}/js/showmsg.js"></script>
     <script type="text/javascript" src="${_path}/js/artDialog.js"></script>
     <script type="text/javascript" src="${_path}/js/jquery.validate-1.13.1.min.js"></script>
     
     <decorator:head />
  </head>
  <body style="overflow:hidden;">
        <%
		    	HttpSession s = request.getSession(); 
			    String userName = ((ManagerUser)s.getAttribute(JEEConstant.SESSION_LOGIN_TOKEN)).getUserName();
			    List<ModuleMenu> modules = (List<ModuleMenu>)s.getAttribute(JEEConstant.SESSION_MODULE);
			    
			    String curModule = "";
			    if(null != s.getAttribute(JEEConstant.SESSION_MODULE_CUR)){
			    	curModule = s.getAttribute(JEEConstant.SESSION_MODULE_CUR).toString();
			    }
			    
		%>
        <div class="top">
			<div class="top_about">	
				<a href="javascript:showmsghelp()" class="help1">使用帮助</a>
				<a href="javascript:showmsgabout()" class="help2">关于</a>
			</div>
			<div class="admin_logo">
				<a><img src="../images/admin_logo.png"></img></a>
			</div>
			<div class="top_nav">
					<ul>
					   <%
					        String curModuleName = "";
					        int index = 0;
						    for(ModuleMenu module: modules){
						    	String className = "";
						    	if(index == 0){
						    		className = "class='first'";
						    	}
						    	
                                if(index == modules.size() - 1){
                                	className = "class='last'";
						    	}
						    	
						    	if(curModule.equals(module.getId())){
						    		curModuleName = module.getMenuName();
						%>
						  <li <%=className%>><a class="selected" href="${_path}/<%=module.getMenuUrl()%>?module=<%=module.getId()%>"><%=module.getMenuName()%></a></li>
						<%	    		
						    	} else{
						%>
						  <li <%=className%>><a href="${_path}/<%=module.getMenuUrl()%>?module=<%=module.getId()%>"><%=module.getMenuName()%></a></li>
						<%   		
						    	}
						    	
						    	index++;
						    }
						    
					    %>
					</ul>
			</div>
			<div class="top_member">
			欢迎您，<span><%=userName%></span> | <a href="javascript:showmsg()">退出</a>
			</div>
			
			<div class="showMsg" id="msgbox" style="text-align:center;display:none;">
				<h5>提示信息</h5>
			    <div class="content guery" style="text-align:left;display:inline-block;display:-moz-inline-stack;zoom:1;*display:inline; max-width:350px">
           您真的要退出，所有配置都完成了吗？
                </div>
			    <div class="bottom">
			    	<a href="javascript:quitsystem()" >坚决退出</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
			    	<a href="javascript:closemsg()" >还没配完</a>
			    </div>
			</div>
			
			<div class="showMsg" id="msgboxabout" style="text-align:center;display:none;">
				<h5>关于</h5>
			    <div class="content guery" style="text-align:left;display:inline-block;display:-moz-inline-stack;zoom:1;*display:inline; max-width:350px">
            嗨拍后台管理系统
              &nbsp;&nbsp;版本: beta1.0
              &nbsp;&nbsp;Copyright © 2015, 成都科意隆科技有限公司 
                </div>
			    <div class="bottom">
			    	<a href="javascript:closemsgabout()" >关闭</a>
			    </div>
			</div>
			<script>
			    function showmsgabout(){
				  document.getElementById("msgboxabout").style.display="block";
				}

				function closemsgabout(){
				  document.getElementById("msgboxabout").style.display="none";
				}
			</script>
			
			<div class="showMsg" id="msgboxhelp" style="text-align:center;display:none;">
				<h5>使用帮助</h5>
			    <div class="content guery" style="text-align:left;display:inline-block;display:-moz-inline-stack;zoom:1;*display:inline; max-width:350px">
             如您在使用过程中有任何问题，请联系信息部！
                </div>
			    <div class="bottom">
			    	<a href="javascript:closemsghelp()" >关闭</a>
			    </div>
			</div>
			<script>
			    function showmsghelp(){
				  document.getElementById("msgboxhelp").style.display="block";
				}

				function closemsghelp(){
				  document.getElementById("msgboxhelp").style.display="none";
				}
			</script>
			
		</div>
		<div class="side_switch" id="side_switch"></div>
		<div class="side_switchl" id="side_switchl"></div>
		
		<div class="left">
			<div class="left_title"><%=curModuleName%>操作菜单</div>
		
     <decorator:body />
  </body>
</html>

<script type="text/javascript">
function quitsystem(){
  window.location='loginout';
}
</script>