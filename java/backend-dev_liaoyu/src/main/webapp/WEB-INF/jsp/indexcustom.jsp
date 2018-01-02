<%@page import="com.kyl.ps.model.image.FolderNameEnum"%>
<%@page import="com.kyl.ps.util.BeanHolder"%>
<%@page import="com.kyl.ps.model.config.CustomMenuChild"%>
<%@page import="com.kyl.ps.model.config.CustomMenu"%>
<%@page import="com.kyl.ps.jee.JEEConstant"%>
<%@page import="java.util.List"%>
<%@page import="com.kyl.ps.model.manageruser.ManagerUser"%>
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/_decorators/base.jsp" %>

<html> 
	<head><title></title></head> 
	<body style="overflow:hidden;">
	    <%
		    	HttpSession s = request.getSession(); 
			    List<CustomMenu> menus = (List<CustomMenu>)s.getAttribute(JEEConstant.SESSION_MODULE_MENU);
		%>

			<ul class="side">
			    <%
			    int i = 1;
			    String menuName = "none";
				 for(CustomMenu menu: menus){
					 menuName = FolderNameEnum.getNameByField(menu.getTag());
				%>
				 <li><a onclick="javascript:ShowFLT(<%=i%>)" href="javascript:void(null)"><%=menuName%></a>
				<% 
				    if(i == 1){
			    	%>
			    	 <div class="xiala" id="LM<%=i%>">
			    	<%
			    	}else{
			    	%>	
			    		<div class="xiala" id="LM<%=i%>" style="display:none">
			    	<%
			    	}	
				
				    int j = 1;
				    for(CustomMenuChild menuChild: menu.getMenuChilds()){
				    	
				      if(i == 1 && j == 1){
				      %>
				      <ol>
					   <a style="color:#ffffff" class="selected" target="main" href="${_path}/image/list?tag=<%=menu.getTag()%>&dateStr=<%=menuChild.getDateStr()%>&menu=<%=menu.getTag()%>">
					  <%
				      } else{
				      %>
					  <ol>
					   <a target="main" href="${_path}/image/list?tag=<%=menu.getTag()%>&dateStr=<%=menuChild.getDateStr()%>&menu=<%=menu.getTag()%>">
					  <%}%>
					   <%=menuChild.getDateStr()%>
					   </a>
					  </ol>
				<%   
				     j++;
				    }
		        %>
		        	</div>
		    	</li> 
			    <%
			     i++;
			    }
			    	String firstMenuTag = menus.get(0).getTag();
		        	String firstMenuDate = menus.get(0).getMenuChilds().get(0).getDateStr();
		        	String menuId = menus.get(0).getTag();
			    %>
			   
			</ul>
			<ul class="side catsub">
			<li class="feed"><a target="_blank" href="http://www.coelong.com">Copyright © coelong</a></li>
			</ul>
		</div>
		
		<div class="right">
		  <IFRAME style="OVERFLOW:visible" id="main" name="main" src="${_path}/image/list?tag=<%=firstMenuTag%>&dateStr=<%=firstMenuDate%>&menu=<%=menuId%>" frameBorder=0 width="100%" scrolling="yes" height="100%"></IFRAME>
		</div>
     <script type="text/javascript">
		var number=<%=menus.size()%>;
		
		function LMYC() {
		var lbmc;
		    for (i=1;i<=number;i++) {
		        lbmc = eval('LM' + i);
		        lbmc.style.display = 'none';
		    }
		}
		 
		function ShowFLT(i) {
		    lbmc = eval('LM' + i);
		    if (lbmc.style.display == 'none') {
		        LMYC();
		        lbmc.style.display = '';
		    }
		    else {
		        lbmc.style.display = 'none';
		    }
		}
	</script>
  	</body>
</html>

<script type="text/javascript">
jQuery(function() {
	jQuery(".side > li > div > ol").on("click", "a", function() {
		$(".side > li > div > ol > a").each(function(){
			jQuery(this).removeClass("selected");
			jQuery(this).css('color','');
		});
		jQuery(this).addClass("selected");
		jQuery(this).css('color','#ffffff');
	})
});
</script>