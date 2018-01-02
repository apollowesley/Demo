<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/_decorators/base.jsp"%>
<page:apply-decorator name="frame">
	<html>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<head>
<script type="text/javascript" src="${_path}/js/jiaose.js"></script>
<title>新增/编辑用户</title>
</head>
<body>
	<form action="${_path}/account/accountedit" method="post"
		id="accountForm">
		<input type="hidden" id="token_" name="token_" value="${sessionScope.token_}" />
		<div class="body">
			<div class="top_subnav">${sessionScope.breadcrumb}</div>
			<div class="navtop">新增用户</div>

			<div class="addpage_con">
				<ul>
					<li class="biaoming">新增用户<font color="red"> *</font></li>
					<li class="addbiao"><input type="hidden" value="${user.id}"
						name="userId" /> <input name="userName" type="text"
						placeholder="请输入用户名" value="${user.userName}" /> </li>
				</ul>

				<ul>
					<li class="biaoming">设置密码<font color="red"> *</font></li>
					<li class="addbiao">
							<input name="password" type="password" value="" />
						</li>
				</ul>
				<ul>
					<li class="biaoming">部门设置<font color="red"> *</font></li>
					<li class="addbiao"><input name="dept" type="text"
						placeholder="请输入部门" value="${user.dept}" /> </li>
				</ul>
				<ul>
					<li class="biaoming">角色设置<font color="red"> *</font></li>
					<li class="addbiao"><select name="roleId">
							<c:forEach var="role" items="${roles}">
								<option ${role.id==user.roleId?'selected':''} value="${role.id}">${role.roleName}</option>
							</c:forEach>
					</select> </li>
				</ul>

				<ul>
					<li class="biaoming">&nbsp;</li>
					<li class="addbiao">
                        <button type="reset" onclick="javascript:history.go(-1)">返回</button>
						<button type="button">提交</button>
					</li>
				</ul>
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
		if($("[name='userId']").val().length == 0 ){
			//设置默认属性
			$.validator.setDefaults({
				submitHandler : function(form) {
					form.submit();
				}
			}), $("#accountForm").validate({
				rules : {
					'userName' : {
						required : true,
						maxlength : 50,
						chrnum : true
					},
					'password' : {
						required : true,
						maxlength : 36,
						minlength : 5
					},
					'dept' : {
						required : true,
						maxlength : 50,
						chrnum : true
					}
				},
				messages : {
					'userName' : {
						required : "请输入账户名称",
						maxlength : "账户名称最多50个字",
						chrnum : "账户名称输入非法"
					},
					'password' : {
						required : "请输入账户密码",
						maxlength : "账户密码最多36个字",
						minlength : "账户密码最短5个字"
					},
					'dept' : {
						required : "请输入部门名称",
						maxlength : "部门名称最多50个字",
						chrnum : "部门名称输入非法"
					}
				},

			//指定错误信息位置
			});
		}else{
			//设置默认属性
			$.validator.setDefaults({
				submitHandler : function(form) {
					form.submit();
				}
			}), $("#accountForm").validate({
				rules : {
					'userName' : {
						required : true,
						maxlength : 50,
						chrnum : true
					},
					'password' : {
						maxlength : 36,
						minlength : 5
					},
					'dept' : {
						required : true,
						maxlength : 50,
						chrnum : true
					}
				},
				messages : {
					'userName' : {
						required : "请输入账户名称",
						maxlength : "账户名称最多50个字",
						chrnum : "账户名称输入非法"
					},
					'password' : {
						maxlength : "账户密码最多36个字",
						minlength : "账户密码最短5个字"
					},
					'dept' : {
						required : "请输入部门名称",
						maxlength : "部门名称最多50个字",
						chrnum : "部门名称输入非法"
					}
				},

			//指定错误信息位置
			});
		}

		$("button[type='button']").click(function() {	
			$("#accountForm").submit();
		});
	});
</script>
<script language=javascript id=clientEventHandlersJS>
	var number = 2;

	function LMYC() {
		var lbmc;
		//var treePic;
		for (i = 1; i <= number; i++) {
			lbmc = eval('LM' + i);
			//treePic = eval('treePic'+i);
			//treePic.src = 'images/file.gif';
			lbmc.style.display = 'none';
		}
	}

	function ShowFLT(i) {
		lbmc = eval('LM' + i);
		//treePic = eval('treePic' + i)
		if (lbmc.style.display == 'none') {
			LMYC();
			//treePic.src = 'images/nofile.gif';
			lbmc.style.display = '';
		} else {
			//treePic.src = 'images/file.gif';
			lbmc.style.display = 'none';
		}
	}
</script>