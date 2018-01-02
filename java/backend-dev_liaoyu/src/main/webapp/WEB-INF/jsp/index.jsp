<%@page import="com.kyl.ps.model.config.ModuleMenu"%>
<%@page import="java.util.List"%>
<%@page import="com.kyl.ps.jee.JEEConstant"%>
<%@page import="com.kyl.ps.model.manageruser.ManagerUser"%>
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/_decorators/base.jsp" %>
<!--  
<page:apply-decorator name="main"> -->
<html> 
	<head><title></title></head> 
	<body style="overflow:hidden;">
        <%
		    	HttpSession s = request.getSession(); 
			    List<ModuleMenu> menus = (List<ModuleMenu>)s.getAttribute(JEEConstant.SESSION_MODULE_MENU);
		%>
			<ul class="side">
			    <%
					int i = 1;   	
				    for(ModuleMenu menu: menus){
				     if(i == 1){
				     %>
				       <li>
				        <a class="selected" target="main" href="${_path}/<%=menu.getMenuUrl()%>?menu=<%=menu.getId()%>">
					 <%
				      } else{
				     %>
				       <li>
				       <a target="main" href="${_path}/<%=menu.getMenuUrl()%>?menu=<%=menu.getId()%>">
					 <%}%>
				      <%=menu.getMenuName()%>
				     </a>
				    </li>
				<%   
				    i++;
				    }
			    
			        String firstMenuUrl = menus.get(0).getMenuUrl();
			        String menuId = menus.get(0).getId();
			    %>
			</ul>
		</div>
		
		<div class="right">
		  <IFRAME style="OVERFLOW:visible" id="main" name="main" src="${_path}/<%=firstMenuUrl%>?menu=<%=menuId%>" frameBorder=0 width="100%" scrolling="yes" height="100%"></IFRAME>
		</div>
     
  	</body>
</html>
<!-- 
</page:apply-decorator> -->

<script type="text/javascript">
jQuery(function() {
	jQuery(".side > li").on("click", "a", function() {
		$(".side > li > a").each(function(){
			jQuery(this).removeClass("selected");
		});
		jQuery(this).addClass("selected");
	})
});
</script>