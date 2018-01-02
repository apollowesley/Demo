<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/_decorators/base.jsp"%>
<page:apply-decorator name="frame">
	<html>
<head>
<title>后台账户列表</title>
</head>
<body class="right_body">
	<div class="body">
	<form action="${_path}/account/accounts">
		<div class="top_subnav">${sessionScope.breadcrumb}</div>

		<div class="nav">
			<ul>
				<button type="submit">搜索</button>
			</ul>
			<ul>
				账号：
				<input name="userName" type="text"  value="${sessionScope.USERNAME}"/>
			</ul>
		</div>
		<div class="tablelist">
			<table class="table">
				<tbody>

					<tr>
						<th colspan="6" class="top_th"><a href="${_path}/account/goacconutedit"
							class="add"><em>添加用户</em></a></th>
					</tr>
					<tr>
						<th>用户名</th>
						<th>部门</th>
						<th>所属角色</th>
						<th>状态</th>
						<th>添加时间</th>
						<th>操作</th>
					</tr>
					<c:forEach var="user" items="${page.rows}">
							<tr>
							<td>${user.userName}</td>
							<td>${user.dept}</td>
							<td>${user.roleName}</td>
							<td><c:if test="${user.status == '0'}">正常</c:if><c:if test="${user.status == '1'}">不正常</c:if> </td>
							<td><a href="${_path}/account/goacconutedit?userId=${user.id}">修改</a>&nbsp;<a href="${_path}/account/deleteacconut?userId=${user.id}">删除</a></td>
							</tr>
					</c:forEach>
				</tbody>
			</table>
			<mypaging:page pageSize="${page.pageSize}" url="accounts" />
		</div>
		</form>
	</div>
</body>
	</html>
</page:apply-decorator>