/**
 * Created by xiezhigang on 17/1/13.
 */

function getIndustryType() {
    area = document.getElementById("area");
    cmbProvince = document.getElementById("cmbProvince");
    cmbCity = document.getElementById("cmbCity");
    cmbArea = document.getElementById("cmbArea");
    str = area.value + "-" + cmbProvince.value + "-" + cmbCity.value + "-" + cmbArea.value;
    $("#jobType").val(jobArray[str]);
}

function cmbSelect(cmb, str){
    var cmb = cmb[0];
    for(var i=0; i<cmb.options.length; i++){
        if(cmb.options[i].value == str){
            cmb.selectedIndex = i;
            if (cmb.onchange != null) {
                cmb.onchange();
            }
            return;
        }
    }
}
$().ready(function () {

     // 营业执照长期选择
    $("#licenseInp").change(function () {
        if ($('#licenseInp').is(":checked") == true) {
            //结束时间消失
            $('#create_at_end').css('display', 'none');
        } else {
            $('#create_at_end').css('display', 'block');
        }
    });

    //行业类别初始化
    addressInit('area', 'cmbProvince', 'cmbCity', 'cmbArea');
    if ((cmb_area || cmb_province || cmb_city || cmb_cmbArea) != "None" && (cmb_area || cmb_province || cmb_city || cmb_cmbArea) != "") {
        cmbSelect($("#area"), cmb_area);
        cmbSelect($('#cmbProvince'), cmb_province);
        cmbSelect($('#cmbCity'), cmb_city);
        cmbSelect($('#cmbArea'), cmb_cmbArea);

    }
    setInterval('getIndustryType()', 500);


    function formatRepo(repo) {
        if (repo.loading) return repo.text;
        markup = "<span selectvalue='" + repo.id + "'>" + repo.bank_name + "</span>";
        return markup;
    }

    function formatRepoSelection(repo) {
        return repo.bank_name || repo.text || repo.id
    }

    $("#bankNo").select2({
        language: 'zh-CN',
        ajax: {
            url: "/dist/inlet/mch/bank",
            type: "GET",
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term,
                    page: params.page
                };
            },
            processResults: function (data, params) {
                params.page = params.page || 1;
                return {
                    results: data.data,
                    pagination: {
                        more: (params.page * 10) < data.total_count
                    }
                };
            },
            cache: true
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        minimumInputLength: 1,
        templateResult: formatRepo,
        templateSelection: formatRepoSelection
    });

    //上传图片正面
    $("#pic1").click(function () {

        //隐藏了input:file样式后，点击头像就可以本地上传
        $("#imgCardFront").click();
        $("#imgCardFront").on("change", function (event) {
            var files = event.target.files, file;
            if (files && files.length > 0) {
                file = files[0];

                //上传传功,清除掉超过显示
                $(".imgSize").remove();
                if (file.size > 1024 * 1024 * 0.3) {
                    $("#imgCardFront").after('<span class="imgSize">图片大小不能超300k!<span>');
                    return false;
                }
            }
            //获取图片的路径，该路径不是图片在本地的路径
            var objUrl = getObjectURL(this.files[0]);
            if (objUrl) {
                //将图片路径存入src中，显示出图片
                $("#pic1").attr("src", objUrl);
            }
        });
    });

    //上传图片反面
    $("#pic2").click(function () {

        //隐藏了input:file样式后，点击头像就可以本地上传
        $("#imgCardBack").click();
        $("#imgCardBack").on("change", function (event) {
            var files = event.target.files, file;
            if (files && files.length > 0) {
                file = files[0];

                //上传传功,清除掉超过显示
                $(".imgSize").remove();
                if (file.size > 1024 * 1024 * 0.3) {
                    $("#imgCardBack").after('<span class="imgSize">图片大小不能超过300k!<span>')
                    return false;
                }
            }
            //获取图片的路径，该路径不是图片在本地的路径
            var objUrl = getObjectURL(this.files[0]);
            if (objUrl) {
                //将图片路径存入src中，显示出图片
                $("#pic2").attr("src", objUrl);
            }
        });
    });
//      上传手持身份照
    $("#img_with_id_card1").click(function () {

        //隐藏了input:file样式后，点击头像就可以本地上传
        $("#img_with_id_card").click();
        $("#img_with_id_card").on("change", function (event) {
            var files = event.target.files, file;
            if (files && files.length > 0) {
                file = files[0];

                //上传传功,清除掉超过显示
                $(".imgSize").remove();
                if (file.size > 1024 * 1024 * 0.3) {
                    $("#img_with_id_card").after('<span class="imgSize">图片大小不能超过300kb<span>')
                    return false;
                }
            }

            //获取图片的路径，该路径不是图片在本地的路径
            var objUrl = getObjectURL(this.files[0]);
            if (objUrl) {
                //将图片路径存入src中，显示出图片
                $("#img_with_id_card1").attr("src", objUrl);
            }
        });
    });

    //经营执照照片
    $("#pic3").click(function () {

        //隐藏了input:file样式后，点击头像就可以本地上传
        $("#licenseImg").click();
        $("#licenseImg").on("change", function (event) {
            var files = event.target.files, file;
            if (files && files.length > 0) {
                file = files[0];

                //上传传功,清除掉超过显示
                $(".imgSize").remove();
                if (file.size > 1024 * 1024 * 0.5) {
                    $("#licenseImg").after('<span class="licenseSiz">图片大小不能超过500kb<span>')
                    return false;
                }
            }
            //获取图片的路径，该路径不是图片在本地的路径
            var objUrl = getObjectURL(this.files[0]);
            if (objUrl) {
                //将图片路径存入src中，显示出图片
                $("#pic3").attr("src", objUrl);
            }
        });
    });

    //收银台照片
    $("#pic4").click(function () {

        //隐藏了input:file样式后，点击头像就可以本地上传
        $("#mch_desk_img").click();
        $("#mch_desk_img").on("change", function (event) {
            var files = event.target.files, file;
            if (files && files.length > 0) {
                file = files[0];

                //上传传功,清除掉超过显示
                $(".imgSize").remove();
                if (file.size > 1024 * 1024 * 0.5) {
                    $("#mch_desk_img").after('<span class="licenseSiz">图片大小不能超过500kb<span>')
                    return false;
                }
            }
            //获取图片的路径，该路径不是图片在本地的路径
            var objUrl = getObjectURL(this.files[0]);
            if (objUrl) {
                //将图片路径存入src中，显示出图片
                $("#pic4").attr("src", objUrl);
            }
        });
    });

    //门店门口照片
    $("#pic5").click(function () {

        //隐藏了input:file样式后，点击头像就可以本地上传
        $("#mch_front_img").click();
        $("#mch_front_img").on("change", function (event) {
            var files = event.target.files, file;
            if (files && files.length > 0) {
                file = files[0];

                //上传传功,清除掉超过显示
                $(".imgSize").remove();
                if (file.size > 1024 * 1024 * 0.5) {
                    $("#mch_front_img").after('<span class="licenseSiz">图片大小不能超过500kb<span>')
                    return false;
                }
            }
            //获取图片的路径，该路径不是图片在本地的路径
            var objUrl = getObjectURL(this.files[0]);
            if (objUrl) {
                //将图片路径存入src中，显示出图片
                $("#pic5").attr("src", objUrl);
            }
        });
    });

    //门店内部照片
    $("#pic6").click(function () {

        //隐藏了input:file样式后，点击头像就可以本地上传
        $("#mch_inner_img").click();
        $("#mch_inner_img").on("change", function (event) {
            var files = event.target.files, file;
            if (files && files.length > 0) {
                file = files[0];

                //上传传功,清除掉超过显示
                $(".imgSize").remove();
                if (file.size > 1024 * 1024 * 0.5) {
                    $("#mch_inner_img").after('<span class="licenseSiz">图片大小不能超过500kb<span>')
                    return false;
                }
            }
            //获取图片的路径，该路径不是图片在本地的路径
            var objUrl = getObjectURL(this.files[0]);
            if (objUrl) {
                //将图片路径存入src中，显示出图片
                $("#pic6").attr("src", objUrl);
            }
        });
    });

    $("#licensePeriod").change(function(event){
        // event.preventDefault();
        if($(this).is(":checked")) {
            $("#licenseEndDate-div").hide();
            $("#licenseEndDate").val('');
        } else {
            $("#licenseEndDate-div").show();
        }
    });

    if($("#licensePeriod").is(":checked")) {
        $("#licenseEndDate-div").hide();
    };

    //-------------制约日期--------------
    $('#licenseStartDate').datetimepicker({
        language: "zh-CN",
        format: "yyyy-mm-dd",
        autoclose: true,
        minView: "month",
        maxView: "decade",
        todayBtn: true
    }).on('blur change dp.hide dp.show', function(e){
        $('#licenseStartDate-div').bootstrapValidator('revalidateField', 'license_start_date');
    });
    $('#licenseEndDate').datetimepicker({
        language: "zh-CN",
        format: "yyyy-mm-dd",
        autoclose: true,
        minView: "month",
        maxView: "decade",
        // endDate: new Date(),
        todayBtn: true
    }).on('blur change dp.hide dp.show', function(e){
        $('#licenseEndDate-div').bootstrapValidator('revalidateField', 'license_end_date');
    });

    //建立一個可存取到該file的url
    function getObjectURL(file) {
        var url = null;
        if (window.createObjectURL != undefined) {
            url = window.createObjectURL(file);
        } else if (window.URL != undefined) {
            // 火狐
            url = window.URL.createObjectURL(file);
        } else if (window.webkitURL != undefined) {
            // 谷歌
            url = window.webkitURL.createObjectURL(file);
        }
        return url;
    }


    $('form').bootstrapValidator({
        message: '不可操作',
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        fields: {
            mchName: {
                message: '商户名验证失败',
                validators: {
                    notEmpty: {
                        message: '商户名不能为空'
                    },
                    stringLength: {
                        min: 1,
                        max: 50,
                        message: '商户名长度必须在1到50位之间'
                    }
                }
            },
            mchShortName: {
                message: '商户简称长度为1~50位',
                validators: {
                    notEmpty: {
                        message: '商户简称不能为空'
                    },
                    stringLnegth: {
                        min: 1,
                        max: 50,
                        message: '商户简称长度必须在1到50位之间'
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
            servicePhone: {
                message: '无效的客服电话',
                validators: {
                    notEmpty: {
                        message: '客服电话不能为空'
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
                message: '无效身份证号码',
                validators: {
                    notEmpty: {
                        message: '身份证号码不能为空'
                    },
                    stringLength: {
                        min: 1,
                        max: 20,
                        message: '无效身份证号码'
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
            }
        }
    })
});
