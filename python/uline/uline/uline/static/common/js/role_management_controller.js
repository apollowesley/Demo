
;(function($){
    var modalType = '',
        modalRoleId = '',
        platform_permits = '',
        sub_platform_permits = '';

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

    function ajaxResponsePromiseJson(request_url,request_data,request_type){
        if(request_type == 'POST'){
            var xsrf=getCookie("_xsrf");
        }

        return $.ajax({
            headers: {"X-XSRFToken":xsrf},
            type:request_type || 'GET',
            url:request_url,
            contentType: "application/json; charset=utf-8",
            data:JSON.stringify(request_data),
            dataType:'json',
            error:function(){
                errorTip('网络出错，请重试！')
            }
        })
    }

    var roleServices={
        'getAddInfo':function(request_data){
            var params=request_data;
            var url='/common/role/permit';
            return ajaxResponsePromise(url,params);
        },//新增--获取权限列表
        'addRole':function(request_data){
            var params=request_data;
            var url='/common/role';
            return ajaxResponsePromise(url,params,'POST');
        },//新增--提交
        'updateRole':function(request_data){
            var params=request_data;
            var url='/common/role';
            return ajaxResponsePromise(url,params,'PUT');
        },//修改--提交
        'deleteRole':function(request_data){
            var params=request_data;
            var url='/common/role';
            return ajaxResponsePromise(url,params,'DELETE');
        },//删除--提交

    };


    //click
    $(document).on('click','[data-click]',function(e) {
        e.stopPropagation();
        e.preventDefault();

        var self = $(this),
            name = $(this).data('click');

        switch (name) {

            case 'getAddInfo':
                $('.role-choose-list input').val('');
                $('#addModal').find('[name="name"]').val(self.attr('role_name'));
                $('.change-error').html('');
                var _params={
                    role_id:self.attr('role_id')
                };
                roleServices.getAddInfo(_params).then(function(res){
                    if(res.code==200){
                        var has_permits=res.data.has_permits;
                        platform_permits=res.data.platform_permits;
                        sub_platform_permits=res.data.sub_platform_permits;

                        if(self.attr('role_type')=='info'){ //查看权限
                            if(has_permits.length==0){
                                errorTip('该角色暂无任何权限');
                                return false;
                            }
                            for(var i=0;i<has_permits.length;i++){
                                $('[data-url$="'+has_permits[i].model_url+'"]').parents('li').show().addClass('on');
                                $('[data-url$="'+has_permits[i].model_url+'"]').parents('ul').show();
                                $('#infoModal input').hide();
                            }
                            $('#infoModal').modal('show');
                        }else{   // 新增、修改
                            var roleList= platform_permits.length>0 ? platform_permits : sub_platform_permits;
                            for(var i=0;i<roleList.length;i++){
                                $('[data-url$="'+roleList[i].model_url+'"]').val(roleList[i].id);
                                $('[data-url$="'+roleList[i].model_url+'"]').parents('li').show();
                            }
                            if(_params.role_id==''){
                                $('#addModal').find('.modal-title').html('新增角色');
                                modalType='add';
                                modalRoleId='';
                                $('.role-where').show();
                                $('.role-where input').eq(0).click();
                            }else{
                                $('#addModal').find('.modal-title').html('修改角色');
                                $('.role-where').hide();
                                modalType='update';
                                modalRoleId=_params.role_id;
                                for(var i=0;i<has_permits.length;i++){
                                    $('[data-url$="'+has_permits[i].model_url+'"]').click();
                                    $('[data-url$="'+has_permits[i].model_url+'"]').parents('li').addClass('on');
                                    $('[data-url$="'+has_permits[i].model_url+'"]').parents('ul').show();
                                }
                            }
                            $('#addModal').modal('show');
                        }
                    }
                });
                break;

            case 'addRole':
                var box=$('#addModal');
                var _params={
                    name:box.find('[name="name"]').val(),
                    permits:[],
                    role_id:modalRoleId,
                };


                $('#addModal .role-choose-list input').each(function(){
                    if($(this).is(':checked') && $(this).val()!=''){
                        _params.permits.push($(this).val());
                    }
                });
                _params.permits=JSON.stringify(_params.permits);
                if(_params.name==''){
                    $('.change-error').html('请填写角色名称');
                    return false;
                }
                if(_params.permits=='[]'){
                    $('.change-error').html('请勾选权限选择');
                    return false;
                }
                if(modalType=='add'){
                    if(sys_type_code=='mr'){
                        _params.is_follower=$("input[name='staff']:checked").val();
                    }
                    roleServices.addRole(_params).then(function(res){
                        if(res.code==200){
                            errorTip('新增成功');
                            box.modal('hide');
                            setTimeout(function(){
                                window.location.reload();
                            },1500);
                        }else{
                            $('.change-error').html(res.msg);
                        }
                    });
                }else{
                    roleServices.updateRole(_params).then(function(res){
                        if(res.code==200){
                            errorTip('修改成功');
                            box.modal('hide');
                            setTimeout(function(){
                                window.location.reload();
                            },1500);
                        }else{
                            $('.change-error').html(res.msg);
                        }
                    });
                }
                break;

            case 'deleteRole':
                var _params={
                    role_id:self.attr('role_id')
                };
                $('body').ulaiberLoading({
                    loadingTitle:'确认删除角色吗？',
                    loadingText:'您正在删除角色：<span class="text-danger">'+self.attr("role_name")+'</span>，删除角色后，已配置该角色的员工将同步删除该角色。',
                    loadingType:'comfirm',
                    sureFunction:function(){
                        roleServices.deleteRole(_params).then(function(res){
                            if(res.code==200){
                                errorTip('删除成功');
                                setTimeout(function(){
                                    window.location.reload();
                                },1500);
                            }else{
                                errorTip(res.msg);
                            }
                        });
                    }
                });
                break;







        }
    });

    $('.role-choose-list h3').click(function(){
        $(this).siblings('ul').toggle();
        $(this).parent('li').toggleClass('on');
    });

    function roleChoose(){
        $('.role-choose-list li,.role-menu').hide();
        $('.role-choose-list li').removeClass('on');
        $('.role-choose-list input').each(function(){
            if($(this).is(':checked')){
                $(this).click();
            }
        });
    }

    $('#addModal,#infoModal').on('hidden.bs.modal', function (e) {
        roleChoose();
    });

    $('.role-where input').click(function(){
        roleChoose();
        if($(this).is(':checked')){
            if($(this).val()==0){ //总部
                for(var i=0;i<platform_permits.length;i++){
                    $('[data-url$="'+platform_permits[i].model_url+'"]').next().html(platform_permits[i].model_name);
                    $('[data-url$="'+platform_permits[i].model_url+'"]').val(platform_permits[i].id);
                    $('[data-url$="'+platform_permits[i].model_url+'"]').parents('li').show();
                }
            }else{ //门店
                for(var i=0;i<sub_platform_permits.length;i++){
                    $('[data-url$="'+sub_platform_permits[i].model_url+'"]').next().html(sub_platform_permits[i].model_name);
                    $('[data-url$="'+sub_platform_permits[i].model_url+'"]').val(sub_platform_permits[i].id);
                    $('[data-url$="'+sub_platform_permits[i].model_url+'"]').parents('li').show();
                }
            }
        }
    })




})(jQuery);