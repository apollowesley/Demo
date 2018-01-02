<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
    <%@include file="/WEB-INF/_decorators/base.jsp"%>

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>贴纸模板列表</title>
</head>
<body>

<c:forEach items="${ templates}" var="t">
 ${t.name } -  ${t.prefix }  - ${t.manager_name}
</c:forEach>

</body>
</html>