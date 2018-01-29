/**
 * Created by apple on 12/4/17.
 */
$('#mch_sub_user_form').bootstrapValidator({
        message: '不可操作',
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        fields: {
            login_name: {
                message: '登录账号验证失败',
                validators: {
                    notEmpty: {
                        message: '登录账号不能为空'
                    },
                    stringLength: {
                        min: 1,
                        max: 50,
                        message: '登录账号长度必须在1到50位之间'
                    }
                }
            },
            name: {
                message: '员工名称长度为1~50位',
                validators: {
                    notEmpty: {
                        message: '员工名称不能为空'
                    }
                }
            },
            phone: {
                message: '无效的手机号码',
                validators: {
                    notEmpty: {
                        message: '手机号码不能为空'
                    },
                    stringLength: {
                        min: 11,
                        max: 11,
                        message: '手机号码必须是11位'
                    }
                }
            },
            email: {
                message: '邮箱地址长度为6~64位',
                validators: {
                    notEmpty: {
                        message: '邮箱地址不能为空'
                    },
                    emailAddress: {
                        message: '邮箱地址格式有误'
                    }
                }
            }

        }
    });







