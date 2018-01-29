/**
 * Created by xiezhigang on 16/11/14.
 */
$('form').bootstrapValidator({
    message: '不可操作',
    feedbackIcons: {
        valid: 'glyphicon glyphicon-ok',
        invalid: 'glyphicon glyphicon-remove',
        validating: 'glyphicon glyphicon-refresh'
    },
    fields: {
        dtName: {
            message: '渠道商名称验证失败',
            validators: {
                notEmpty: {
                    message: '渠道商名称不能为空'
                },
                stringLength: {
                    min: 1,
                    max: 50,
                    message: '渠道商名称长度必须在1到50位之间'
                }
            }
        },
        jobType: {
            message: '无效的行业类别',
            validators: {
                notEmpty: {
                    message: '行业类别不能为空'
                }
            }
        },
        province: {
            message: '无效的省份名字',
            validators: {
                notEmpty: {
                    message: '省份不能为空'
                }
            }
        },
        city: {
            message: '无效的城市名字',
            validators: {
                notEmpty: {
                    message: '城市不能为空'
                }
            }
        },
        address: {
            message: '无效的地址',
            validators: {
                notEmpty: {
                    message: '地址不能为空'
                }
            }
        },
        contact: {
            message: '无效的联系人',
            validators: {
                notEmpty: {
                    message: '联系人不能为空'
                }
            }
        },
        mobile: {
            message: '无效的联系电话',
            validators: {
                notEmpty: {
                    message: '联系电话不能为空'
                },
                stringLength: {
                    min: 11,
                    max: 11,
                    message: '联系电话必须是11位'
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
        },
        balanceType: {
            message: '无效的交易类型',
            validators: {
                notEmpty: {
                    message: '交易类型不能为空'
                }
            }
        },
        balanceName: {
            message: '无效的结算户名',
            validators: {
                notEmpty: {
                    message: '结算户名不能为空'
                }
            }
        },
        bankNo: {
            message: '无效的结算银行',
            validators: {
                notEmpty: {
                    message: '结算银行不能为空'
                }
            }
        },
        bankName: {
            message: '无效的结算银行',
            validators: {
                notEmpty: {
                    message: '结算银行不能为空'
                }
            }
        },
        balanceNo: {
            message: '无效的结算账户',
            validators: {
                notEmpty: {
                    message: '结算账户不能为空'
                }
            }
        },
        idCard: {
            message: '身份证号码长度为15/18位',
            validators: {
                notEmpty: {
                    message: '身份证号码不能为空'
                },
                stringLength: {
                    min: 15,
                    max: 18,
                    message: '身份证号码为15/18位'
                }
            }
        },
        imgCardFront: {
            message: '上传身份证正面失败',
            validators: {
                notEmpty: {
                    message: '身份证正面不能为空'
                },
                file: {
                    message: '请上传身份证正面'
                }
            }
        },
        imgCardBack: {
            message: '上传身份证反面失败',
            validators: {
                notEmpty: {
                    message: '身份证反面不能为空'
                },
                file: {
                    message: '请上传身份证反面'
                }
            }
        },
        'checkItem[]': {
            validators: {
                choice: {
                    min: 1,
                    max: 9,
                    message: '请输入其中一种支付方式的费率'
                }
            }
        }
    }
});