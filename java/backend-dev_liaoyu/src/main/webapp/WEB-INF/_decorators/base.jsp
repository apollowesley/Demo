<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="spring" uri="http://www.springframework.org/tags" %>
<%@ taglib prefix="c" uri="/WEB-INF/tlds/c.tld" %> 
<%@ taglib prefix="mypaging" uri="/WEB-INF/tlds/page.tld" %>

<%
final String path = request.getContextPath();
request.setAttribute("_path",path);
%>
