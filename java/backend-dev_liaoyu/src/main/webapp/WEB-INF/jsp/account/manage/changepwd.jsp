<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/_decorators/base.jsp"%>
<page:apply-decorator name="frame">
	<html>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<head>
<title>修改密码</title>
</head>
<body>
	<form action="${_path}/account/changepassword" method="post" id="accountForm">
		<input type="hidden" id="token_" name="token_" value="${sessionScope.token_}" />
		<div class="body">
			<div class="top_subnav">${sessionScope.breadcrumb}</div>
			<div class="navtop">修改密码</div>

			<div class="addpage_con">
				<ul>
					<li class="biaoming">原密码<font color="red"> *</font></li>
					<li class="addbiao"><input name="orgpassword" type="password" value="" /> </li>
				</ul>

				<ul>
					<li class="biaoming">新密码<font color="red"> *</font></li>
					<li class="addbiao">
							<input name="password" type="password" value="" />
						</li>
				</ul>
				<ul>
					<li class="biaoming">&nbsp;</li>
					<li class="addbiao">
						<button  type="button">提交</button>
					</li>
				</ul>
				<div id="error" class="error">${msg}</div>
			</div>
		</div>
	</form>
</body>
	</html>
</page:apply-decorator>
<script type="text/javascript">
	$(document).ready(function() {
		
		jQuery.validator.addMethod("chrnum", function(value, element) {
			var chrnum = /^([\a-\z\A-\Z0-9\u4E00-\u9FA5\ ]+)$/;
			return this.optional(element) || (chrnum.test(value));
		});

		//设置默认属性
		$.validator.setDefaults({
			submitHandler : function(form) {
				form.submit();
			}
		}), $("#accountForm").validate({
			rules : {
				'orgpassword' : {
					required : true,
					maxlength : 36,
					minlength : 5
				},
				'password' : {
					required : true,
					maxlength : 36,
					minlength : 5
				}
			},
			messages : {
				'orgpassword' : {
					required : "请输入原密码",
					maxlength : "账户密码最多36个字",
					minlength : "账户密码最短5个字"
				},
				'password' : {
					required : "请输入新密码",
					maxlength : "账户密码最多36个字",
					minlength : "账户密码最短5个字"
				}
			},

		//指定错误信息位置
		});


		$("button[type='button']").click(function() {	
			$("#accountForm").submit();
		});
	});
</script>