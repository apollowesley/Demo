
;(function($){

    //获取cookie
    function getCookie(name) {
        var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
        return r ? r[1] : undefined;
    };

    //公用请求方法
    function ajaxResponsePromise(request_url,request_data,request_type){
        if(request_type == 'POST'){
            var xsrf=getCookie("_xsrf");
        }

        return $.ajax({
            headers: {"X-XSRFToken":xsrf},
            type:request_type || 'GET',
            url:request_url,
            data:request_data,
            dataType:'json',
            error:function(){
                errorTip('网络出错，请重试！')
            }
        })
    }

    //解密参数
    function getParams() {
        var params = {};
        location.href.replace(/([\w-]+)\=([^\&\=]+)/ig, function (a, b, c) {
            params[b] = c;
        });

        for (var key in params) {
            params[key] = decodeURIComponent(params[key]);
        }
        return params;
    }

    var staffServices={
        'getAddInfo':function(request_data){
            var params=request_data;
            var url='/common/settings/sub_user/add';
            return ajaxResponsePromise(url,params);
        },//新增--获取角色信息
        'addStaff':function(request_data){
            var params=request_data;
            var url='/common/settings/sub_user/add';
            return ajaxResponsePromise(url,params,'POST');
        },//新增--提交员工请求
        'getUpdateInfo':function(request_data){
            var params=request_data;
            var url='/common/settings/sub_user/edit';
            return ajaxResponsePromise(url,params);
        },//修改--获取角色信息
        'updateStaff':function(request_data){
            var params=request_data;
            var url='/common/settings/sub_user/edit';
            return ajaxResponsePromise(url,params,'POST');
        },//修改--提交修改请求
        'getStaffInfo':function(request_data){
            var params=request_data;
            var url='/common/settings/sub_user/info';
            return ajaxResponsePromise(url,params);
        },//查看--员工信息
        'getQrCode':function(request_data){
            var params=request_data;
            var url='/common/settings/sub_user/getqrcode';
            return ajaxResponsePromise(url,params);
        },//获取--临时二维码
        'getWxStatus':function(request_data){
            var params=request_data;
            var url='/common/settings/sub_user/bindingstatus';
            return ajaxResponsePromise(url,params);
        },//判断--是否绑定成功
    };


    //click
    $(document).on('click','[data-click]',function(e) {
        e.stopPropagation();
        e.preventDefault();

        var self = $(this),
            name = $(this).data('click');

        switch (name) {

            case 'getAddInfo':
                $('.change-error').html('');
                var _params={};
                $('#addModal').attr('data-type','add');
                $('#addModal').find('.modal-title').html('新增员工信息');
                $('#addModal').find('input').val('');
                $('#addModal').find('select').val('1');
                staffServices.getAddInfo(_params).then(function(res){
                    if(res.code==200){
                        var roleList=res.role;
                        var csList=res.cs_data;
                        var _html='',csListHtml='',chainHtml='',staffChain=0,staffCs=0;
                        for(var i=0;i<roleList.length;i++){
                            if(roleList[i].is_follower==0){ //0 表示总店
                                staffChain=1;
                                _html+='<li class="role-item-chain"><input type="checkbox" value="'+roleList[i].role_id+'" />'+roleList[i].role_name+'</li>';
                            }else if(roleList[i].is_follower==1){ //0 表示门店
                                staffCs=1;
                                _html+='<li class="role-item-cs"><input type="checkbox" value="'+roleList[i].role_id+'" />'+roleList[i].role_name+'</li>';
                            }
                        }
                        if(staffChain>0){
                            chainHtml+='<li>\n' +
                                    '<input type="radio"  name="staff" value="2"/>\n' +
                                    '<span>总部员工</span>\n' +
                                    '</li>';
                        }
                        if(staffCs>0){
                            chainHtml+='<li>\n' +
                                    '<input type="radio"  name="staff" value="1"/>\n' +
                                    '<span>门店员工</span>\n' +
                                    '</li>';
                        }
                        $('#staffList ul').html(chainHtml);
                        $('#staffList li').eq(0).find('input').click();
                        $('#roleList ul').html(_html);
                        chainChoose();
                        if(sys_type_code=='mr'){
                            $('.base-chain-user-remove-list ul').html('');
                            for(var i=0;i<csList.length;i++){
                                csListHtml+='<li><p data-mch-id="'+csList[i].sys_id+'">'+csList[i].sys_name+'</p><span data-click="cs_add">添加</span></li>';
                            }
                            $('.base-chain-user-add-list ul').html(csListHtml);

                            //门店选择模糊查询
                            $('.search-cs-list').keyup(function(){
                                var val=$(this).val();
                                var _html='';
                                if(val.length>0){
                                    findEach(val,csList);
                                }else{
                                    for(var i=0;i<csList.length;i++){
                                        if($('.base-chain-user-remove-list li').length>0){
                                            $('.base-chain-user-remove-list li').each(function(){
                                                if($(this).find('p').attr('data-mch-id') != csList[i].sys_id){
                                                    _html+='<li><p data-mch-id="'+csList[i].sys_id+'">'+csList[i].sys_name+'</p><span data-click="cs_add">添加</span></li>';
                                                }
                                            });
                                        }else{
                                             _html+='<li><p data-mch-id="'+csList[i].sys_id+'">'+csList[i].sys_name+'</p><span data-click="cs_add">添加</span></li>';
                                        }
                                    }
                                    $('.base-chain-user-add-list ul').html(_html);
                                }
                            });
                        }
                        $('#addModal').modal('show');
                        $('.login-name-tip').html(res.suffix);
                    }
                });
                break;

            //左侧添加操作
            case 'cs_add':
                var val=self.siblings('p').text();
                var mch_id=self.siblings('p').attr('data-mch-id');
                var _html='<li><p data-mch-id="'+mch_id+'">'+val+'</p><span data-click="cs_remove">删除</span></li>';
                self.parents('li').remove();

                $('.base-chain-user-remove-list ul').append(_html);
                break;

            //右侧删除操作
            case 'cs_remove':
                var val=self.siblings('p').text();
                var mch_id=self.siblings('p').attr('data-mch-id');
                var _html='<li><p data-mch-id="'+mch_id+'">'+val+'</p><span data-click="cs_add">添加</span></li>';
                self.parents('li').remove();
                $('.base-chain-user-add-list ul').append(_html);
                break;

            //右侧删除操作
            case 'chainChoose':
                self.attr('checked','checked')
                chainChoose();
                break;

            case 'changeStaff':
                var addBox=$('#addModal');
                var _params={
                    login_name:addBox.find('[name="login_name"]').val()+$('.login-name-tip').html(),
                    name:addBox.find('[name="name"]').val(),
                    phone1:addBox.find('[name="phone1"]').val(),
                    email:addBox.find('[name="email"]').val(),
                    status:addBox.find('[name="status"]').val(),
                    employee_role:[],
                    junior_ids:[],
                    headquarters:'',
                };
                $('#roleList input').each(function(){
                    if($(this).is(':checked')){
                        _params.employee_role.push($(this).val());
                    }
                });
                $('.base-chain-user-remove-list li').each(function(){
                    _params.junior_ids.push($(this).children('p').attr('data-mch-id'));
                });
                _params.employee_role=JSON.stringify(_params.employee_role);
                _params.junior_ids=JSON.stringify(_params.junior_ids);
                if(sys_type_code=='mr'){
                    _params.headquarters=$("input[name='staff']:checked").val();
                }

                var phonereg = /^1[34578]\d{9}$/;
                var emailreg = /^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/;
                if(addBox.find('[name="login_name"]').val()==''){
                    $('.change-error').html('登录账号不能为空');
                    return false;
                }else if(_params.name.length<2 || _params.name.length>64){
                    $('.change-error').html('员工姓名长度必须为2到30个字');
                    return false;
                }else if(_params.phone1=='' || !phonereg.test(_params.phone1)){
                    $('.change-error').html('请输入有效的手机号码');
                    return false;
                }else if(_params.email=='' || !emailreg.test(_params.email)){
                    $('.change-error').html('请输入有效的邮箱地址');
                    return false;
                }

                if(addBox.attr('data-type')=='add'){
                    staffServices.addStaff(_params).then(function(res){
                        if(res.code==200){
                            $('#addModal').modal('hide');
                            errorTip(res.msg);
                            setTimeout(function(){
                                window.location.reload();
                            },1500);
                        }else{
                            var _html='';
                            for(var i=0;i<res.msg.length;i++){
                                _html+='<p>'+res.msg[i]+'</p>';
                            }
                            $('.change-error').html(_html);
                        }
                    });
                }else if(addBox.attr('data-type')=='update'){
                    _params.modify_id=addBox.attr('data-id');
                    staffServices.updateStaff(_params).then(function(res){
                        if(res.code==200){
                            $('#addModal').modal('hide');
                            errorTip('修改成功');
                            setTimeout(function(){
                                window.location.reload();
                            },1500);
                        }else{
                            var _html='';
                            for(var i=0;i<res.msg.length;i++){
                                _html+='<p>'+res.msg[i]+'</p>';
                            }
                            $('.change-error').html(_html);
                        }
                    });
                }
                break;

            case 'getUpdateInfo':
                $('.change-error').html('');
                $('#addModal').attr('data-type','update');
                $('#addModal').attr('data-id',self.attr('modify_id'));
                var _params={
                    modify_id:self.attr('modify_id')
                };
                staffServices.getUpdateInfo(_params).then(function(res){
                    if(res.code==200){
                        console.log(res);
                        var updateBox=$('#addModal');
                        var roleList=res.role;
                        var _html='',leftHtml='',rightHtml='',chainHtml='',staffChain=0,staffCs=0;
                        updateBox.find('.modal-title').html('修改员工信息');
                        for(key in res.profile){
                            updateBox.find('[name="'+key+'"]').val(res.profile[key]);
                        }
                        var login_name=res.profile.login_name.split('@');
                        updateBox.find('[name="login_name"]').val(login_name[0]);
                        $('.login-name-tip').html('@'+login_name[1]);
                        for(var i=0;i<roleList.length;i++){
                            //0 表示总店  1 表示门店
                            _html+='<li '
                            if(roleList[i].is_follower==0) {
                                staffChain=1;
                                _html += 'class="role-item-chain"';
                            }else if(roleList[i].is_follower==1){
                                staffCs=1;
                                _html += 'class="role-item-cs"';
                            }
                            _html+='><input type="checkbox" value="'+roleList[i].role_id+'" ';
                            if(roleList[i].role=='true'){
                                _html+='checked="checked"';
                            }
                            _html+=' />'+roleList[i].role_name+'</li>';
                        }
                        if(staffChain>0){
                            chainHtml+='<li>\n' +
                                    '<input type="radio" name="staff" value="2"/>\n' +
                                    '<span>总部员工</span>\n' +
                                    '</li>';
                        }
                        if(staffCs>0){
                            chainHtml+='<li>\n' +
                                    '<input type="radio" name="staff" value="1"/>\n' +
                                    '<span>门店员工</span>\n' +
                                    '</li>';
                        }
                        $('#staffList ul').html(chainHtml);
                        $('#staffList [value="'+res.headquarters+'"]').click();
                        $('#roleList ul').html(_html);
                        chainChoose();
                        if(res.left_cs || res.right_cs){
                            for(var i=0;i<res.right_cs.length;i++){
                                rightHtml+='<li><p data-mch-id="'+res.right_cs[i].sys_id+'">'+res.right_cs[i].sys_name+'</p><span data-click="cs_remove">删除</span></li>'
                            }
                            $('.base-chain-user-remove-list ul').html(rightHtml);
                            for(var i=0;i<res.left_cs.length;i++){
                                leftHtml+='<li><p data-mch-id="'+res.left_cs[i].sys_id+'">'+res.left_cs[i].sys_name+'</p><span data-click="cs_add">添加</span></li>'
                            }
                            $('.base-chain-user-add-list ul').html(leftHtml);
                        }
                        $('#addModal').modal('show');
                    }
                });
                break;

            case 'getQrCode':
                loadingShow();
                var _params={
                    employee_id:self.attr('employee_id')
                };
                staffServices.getQrCode(_params).then(function(res){
                    loadingHide();
                    if(res.code==200){
                        $('#bindingwx img').attr('src',res.scan_url);
                        $('#bindingwx').modal('show');
                        var params={
                            employee_id:_params.employee_id,
                            binding_status:1,
                        }
                        wxBindStatus(params);
                    }else{
                        errorTip(res.msg);
                    }
                });
                break;

            case 'qrUnBind':
                loadingShow();
                var _params={
                    employee_id:self.attr('employee_id'),
                    binding_status:2,
                };
                wxBindStatus(_params);
                break;

            case 'getStaffInfo':
                var _params={
                    employee_id:self.attr('employee_id')
                };
                staffServices.getStaffInfo(_params).then(function(res){
                    if(res.code==200){
                        var employee_profile=res.employee_profile;
                        var employee_record=res.employee_record;
                        for(key in employee_profile){
                            $('[data-key="'+key+'"]').html(employee_profile[key]);
                        }
                        var _html='';
                        for(var i=0;i<employee_record.length;i++){
                            _html+='<li><p>'+employee_record[i].comment+'</p>\n' +
                                '<span>'+employee_record[i].create_at+'</span>\n' +
                                '<p class="c-999">操作人：'+employee_record[i].name+'（'+employee_record[i].email+'）</p></li>'
                        }
                        $('.staff-record-list ul').html(_html);

                        $('#infoModal').modal('show');
                    }
                });
                break;



        }
    });

    //轮询
    var timer;
    function wxBindStatus(_params){
        loadingHide();
        timer=setInterval(function(){
            staffServices.getWxStatus(_params).then(function(res){
                if( res.code==200 && res.msg =='1' ){
                    $('#bindingwx').modal('hide');
                    errorTip('绑定成功');
                    clearInterval(timer);
                    setTimeout(function(){
                        window.location.reload();
                    },1500)
                }else if( res.code==200 && res.msg =='2' ){
                    errorTip('解绑成功');
                    clearInterval(timer);
                    setTimeout(function(){
                        window.location.reload();
                    },1500)
                }else if(res.code==406){
                    errorTip(res.msg);
                }
            })
        },2000)
    }

    $('#bindingwx').on('hidden.bs.modal', function (e) {
        clearInterval(timer);
    });


    //模糊匹配方法
    function findEach(val,dataList){
        var list=dataList;
        var len = list.length;
        var arr = [];
        var arrstr='';
        var _html='';
        for(var i=0;i<len;i++){
            //如果字符串中不包含目标字符会返回-1
            if(list[i].sys_name.indexOf(val)>=0 || list[i].sys_id.toString().indexOf(val)>=0){
                arrstr='{"sys_name":"'+list[i].sys_name+'","sys_id":"'+list[i].sys_id+'"}';
                arr.push(JSON.parse(arrstr));
            }
        }

        for(var i=0;i<arr.length;i++){
            if($('.base-chain-user-remove-list li').length>0){
                $('.base-chain-user-remove-list li').each(function(){
                    if($(this).find('p').attr('data-mch-id') != arr[i].sys_id){
                        _html+='<li><p data-mch-id="'+arr[i].sys_id+'">'+arr[i].sys_name+'</p><span data-click="cs_add">添加</span></li>';
                    }
                });
            }else{
                 _html+='<li><p data-mch-id="'+arr[i].sys_id+'">'+arr[i].sys_name+'</p><span data-click="cs_add">添加</span></li>';
            }

        }
        $('.base-chain-user-add-list ul').html(_html);
        //return arr;
    }

    $('#staffList').on('click','input',function(){
        chainChoose();
    });

    function chainChoose(){
        $('#staffList input').each(function(){
            if($(this).is(':checked')){
                if($(this).val()==2){
                    $('.role-item-cs').hide();
                    $('.base-chain-user-box').hide();
                    $('.role-item-chain').show();
                }else{
                    $('.role-item-chain').hide();
                    $('.base-chain-user-box').show();
                    $('.role-item-cs').show();
                }
            }
        })
    }

    //所属门店模糊查询
    function formatRepoOne(repo) {
            if (repo.loading) return repo.name;
            markup = "<span>" + repo.name+'('+repo.id+')' + "</span>";
            return markup;
        }

    function formatRepoSelectionOne(repo) {
        return   repo.name ;
    }
    $("#mch_id").select2({
        language: 'zh-CN',
        ajax: {
            url: "/common/settings/sub_user/index/cs",
            type: "GET",
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    query_id_name: params.term,
                    page: params.page
                };
            },
            processResults: function (data, params) {
                params.page = params.page || 1;
                return {
                    results: data.data
                };
            },
            cache: true
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        minimumInputLength: 1,
        templateResult: formatRepoOne,
        templateSelection: formatRepoSelectionOne
    });
    $('#select2-mch_id-container').text(mch_id);



})(jQuery);