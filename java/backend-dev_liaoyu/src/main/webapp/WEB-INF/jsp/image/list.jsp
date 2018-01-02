<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/_decorators/base.jsp"%>
<page:apply-decorator name="frame">
<html>
<head><title>图片管理</title></head>
<body class="right_body">
	<div class="body">
		<div class="top_subnav">${sessionScope.breadcrumb}</div>
		<form action="${_path}/image/list">
         <div class="nav">
         	<ul class="search">
         		<input name="dateStr" type="hidden" value="${dateStr}"/>
	         	<input name="desc" type="text" value="${desc}" placeholder="输入文件名" />
	         	<button></button>
         	</ul>
         </div>
         </form>
        <div class="tablelist">
	      <div class="navtop"> ${dateStr } 图片库&nbsp;&nbsp;</div>
            <div class="imglist_con">
	            <c:forEach var="picture" items="${page.rows}">
	             <li>
	            	<c:if test="${picture.isUsed==0 }">
	            	    <!-- <a href="updateShow?imgId=${picture.id}"> -->
	            	    <a>
	                    <img src="${picture.pictureUrl}" /><p><nobr>${picture.description }</nobr></p>
	            		<em>已引用</em>
	            	</c:if>
	            	<c:if test="${picture.isUsed==1 }">
	            	    <a>
	                     <img src="${picture.pictureUrl}" /><p><nobr>${picture.description }</nobr></p>
	            		<i>未引用</i>
	            	</c:if>
	            	</a>
	           	 </li>
	            </c:forEach>
            </div>
        </div>
		<mypaging:page pageSize="${page.pageSize}" url="list" />
	</div>
	
	<div class="buque"></div>
</body>
</html>
</page:apply-decorator>