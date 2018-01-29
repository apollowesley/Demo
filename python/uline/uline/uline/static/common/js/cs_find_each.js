/**
 * Created by base on 26/6/17.
 */
var sub_user_host=window.location.protocol + '//' + window.location.host;
$(document).on('click','[data-click]',function(e){
    e.stopPropagation();
    e.preventDefault();

    var self=$(this),
        name=$(this).data('click');

    switch (name){

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

        //新增模态框显示
        case 'showAddModal':
            $('.change-error').html('');
            $('#myModal').attr('data-view','add');
            $('#myModal input').val('');
            $('.sub-login-name span').show();
            $('#myModal .modal-title').html('新增员工账号');
            $('.cs-select').hide();
            $('.base-chain-user-remove-list ul').html('');
            searchCsList();
            var csList=searchCsList();
            $('.search-cs-list').keyup(function(){
                var val=$(this).val();
                var _html='';
                if(val.length>0){
                    findEach(val,csList);
                }else{
                    for(var i=0;i<csList.length;i++){
                        if($('.base-chain-user-remove-list li').length>0){
                            $('.base-chain-user-remove-list li').each(function(){
                                if($(this).find('p').attr('data-mch-id') != csList[i].mch_id){
                                    _html+='<li><p data-mch-id="'+csList[i].mch_id+'">'+csList[i].mch_shortname+'</p><span data-click="cs_add">添加</span></li>';
                                }
                            });
                        }else{
                             _html+='<li><p data-mch-id="'+csList[i].mch_id+'">'+csList[i].mch_shortname+'</p><span data-click="cs_add">添加</span></li>';
                        }
                    }
                    $('.base-chain-user-add-list ul').html(_html);
                }
            });
            break;

        //新增(修改)提交保存
        case 'sendCommon':
            sendAddCs($('#myModal').attr('data-view'));
            break;


        //查看
        case 'checkUser':
            $('.change-error').html('');
            $('#checkModal').attr('data-mch-id',self.parents('td').siblings().eq(0).text());
            var val=self.parents('td').siblings().eq(0).text();
            checkUser(val);
            break;

        //编辑
        case 'editUser':
            $('.change-error').html('');
            $('#myModal .modal-title').html('编辑员工账号');
            $('.cs-select').show();
            var val=self.parents('td').siblings().eq(0).text();
            $('#myModal [name="mch_sub_id"]').val(val);
            checkUser(val,'edit');
            break;

    }

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
	    if(list[i].mch_shortname.indexOf(val)>=0 || list[i].mch_id.toString().indexOf(val)>=0){
	        arrstr='{"mch_shortname":"'+list[i].mch_shortname+'","mch_id":"'+list[i].mch_id+'"}';
	        arr.push(JSON.parse(arrstr));
	    }
	}

	for(var i=0;i<arr.length;i++){
	    if($('.base-chain-user-remove-list li').length>0){
	        $('.base-chain-user-remove-list li').each(function(){
                if($(this).find('p').attr('data-mch-id') != arr[i].mch_id){
                    _html+='<li><p data-mch-id="'+arr[i].mch_id+'">'+arr[i].mch_shortname+'</p><span data-click="cs_add">添加</span></li>';
                }
            });
        }else{
	         _html+='<li><p data-mch-id="'+arr[i].mch_id+'">'+arr[i].mch_shortname+'</p><span data-click="cs_add">添加</span></li>';
        }

    }
	$('.base-chain-user-add-list ul').html(_html);
	//return arr;
}

//查询门店信息列表
function searchCsList(){
    var csList;
    var csListHtml='';
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: '/chain/settings/sub_user/add',
        async:false,
        beforeSend: function (XMLHttpRequest) {
        },
        success: function (res) {
            if(res.code == 200){
                csList=res.data;
                for(var i=0;i<csList.length;i++){
                    csListHtml+='<li><p data-mch-id="'+csList[i].mch_id+'">'+csList[i].mch_shortname+'</p><span data-click="cs_add">添加</span></li>';
                }
                $('.base-chain-user-add-list ul').html(csListHtml);
                $('#myModal').modal('show');
            }else{
                errorTip('门店列表查询失败');
            }

        },
        complete: function (XMLHttpRequest, textStatus) {
        },
        error: function (xhr) {
            csList='';
        }
    });
    return csList;
}

//新增(修改)提交方法
function sendAddCs(queryStatus){
    var _html='';
    var mch_id=[];
    if($('.base-chain-user-remove-list li').length=0){
        errorTipBtn('请添加门店');
        return false;
    }
    $('.base-chain-user-remove-list li').each(function(){
        mch_id.push($(this).children('p').attr('data-mch-id'));
    });
    var xsrf=$('input[name="_xsrf"]').val();
    var parent=$('#myModal');
    var _params={
        login_name:parent.find('input[name="login_name"]').val()+parent.find('input[name="login_name"]').siblings('span').text(),
        mch_sub_name:parent.find('input[name="mch_sub_name"]').val(),
        phone:parent.find('input[name="phone"]').val(),
        email:parent.find('input[name="email"]').val(),
        status:parent.find('select[name="status"]').val(),
        mch_id:JSON.stringify(mch_id)
    };
    if(queryStatus=='update'){
        //编辑提交
        var url='/chain/settings/sub_user/edit';
        var txt='修改'
        _params.mch_sub_id=parent.find('input[name="mch_sub_id"]').val();
        _params.login_name=parent.find('input[name="login_name"]').val();

        //修改为禁用时  调用
        if($('#subUserSelect').val() == 2){
           $.ajax({
               type: "get",  //提交方式
               url: sub_user_host + "/chain/settings/sub_user/bindingstatus",//路径
               data: {
                   "mch_sub_id": mch_sub_id,
                   "binding": 2
               },
               success: function (result) {
                   if (result.code == 200 && result.msg == 2) {
                       window.location.reload();
                   } else {
                       errorTipBtn(result.msg)
                   }
               }
           })
        }
    }else{
        //新增提交
        var url='/chain/settings/sub_user/add'
        var txt='新增'
    }
    $.ajax({
        headers: {"X-XSRFToken":xsrf},
        type: 'post',
        dataType: 'json',
        url: url,
        data:_params,
        beforeSend: function (XMLHttpRequest) {
        },
        success: function (res) {
            if(res.code == 200){
                $('#myModal').modal('hide');
                errorTip(txt+'成功');
                setTimeout(function(){
                    window.location=sub_user_host+'/chain/settings/sub_user';
                },2000)
            }else{
                for(i in res.data){
                    _html+='<p>'+res.data[i]+'</p>';
                }
                $('.change-error').html(_html);
            }
        },
        complete: function (XMLHttpRequest, textStatus) {
        },
        error: function (xhr) {
            errorTip(txt+'失败');
        }

    });
}

//查看员工信息
function checkUser(val,checkStatus){
    var url='/chain/settings/sub_user/info';
    var _params={
        mch_sub_id:val
    };
    $.ajax({
        type: 'get',
        dataType: 'json',
        url: url,
        data:_params,
        beforeSend: function (XMLHttpRequest) {
        },
        success: function (res) {
            if(res.code == 200){
                if(checkStatus == 'edit'){
                    var rightHtml='';
                    var leftHtml='';
                    $('#myModal').attr('data-view','update');
                    //编辑--查看
                    $('#myModal').modal('show');
                    $('.sub-login-name span').hide();
                    for(key in res.profile){
                        $('#myModal [name="'+key+'"]').val(res.profile[key]);
                    }
                    for(var i=0;i<res.right_cs_name.length;i++){
                        rightHtml+='<li><p data-mch-id="'+res.right_cs_name[i].mch_id+'">'+res.right_cs_name[i].mch_shortname+'</p><span data-click="cs_remove">删除</span></li>'
                    }
                    $('.base-chain-user-remove-list ul').html(rightHtml);
                    for(var i=0;i<res.left_cs_name.length;i++){
                        leftHtml+='<li><p data-mch-id="'+res.left_cs_name[i].mch_id+'">'+res.left_cs_name[i].mch_shortname+'</p><span data-click="cs_add">添加</span></li>'
                    }
                    $('.base-chain-user-add-list ul').html(leftHtml);
                }else{
                    var _html='';
                    //查看
                    $('#checkModal').modal('show');
                    for(key in res.profile){
                        $('#checkModal [name="'+key+'"]').val(res.profile[key]);
                    }
                    if(res.profile.status){
                        $('.cs-status').html('启用')
                    }else{
                        $('.cs-status').html('禁用')
                    }
                    for(var i=0;i<res.right_cs_name.length;i++){
                        _html+='<span>'+res.right_cs_name[i].mch_shortname+'、</span>'
                    }
                    $('.choose-cs').html(_html);
                }
            }else{
                errorTip('请求失败，稍后重试');
            }
        },
        complete: function (XMLHttpRequest, textStatus) {
        },
        error: function (xhr) {
            errorTip('请求失败，稍后重试');
        }

    });
}


//微信绑定
$('.bind_wx_code').on('click',function() {
    //绑定微信弹出微信二维码窗口
    var mch_sub_id = $(this).attr('bindvalue');
    var cs=$(this).attr('bindCs');
    if(cs=='None'){
        errorTipBtn('该员工未选择门店,暂不能绑定微信,请选择门店后再尝试');
        return false;
    }
    var _this=$(this);
    var binding = 1;
    $.ajax({
        type: "get",  //提交方式
        url: sub_user_host + "/merchant/settings/sub_user/getqrcode",//路径
        data: {
            "mch_sub_id": mch_sub_id
        },//数据，这里使用的是Json格式进行传输
        success: function (result) {//返回数据根据结果进行相应的处理
            if (result.code == 200) {
                $('#bindingwx').modal('show');
                $('#qrimg').attr('src', result.scan_url);

            } else {
                clearInterval(timer);
                errorTipBtn(result.msg)

            }
        }
    });
    var timer=setInterval(function(){
        $.ajax({
            type: "get",  //提交方式
            url: sub_user_host + "/merchant/settings/sub_user/bindingstatus",//路径
            data: {
                "mch_sub_id": mch_sub_id,
                "binding": 1
            },//数据，这里使用的是Json格式进行传输
            success: function (result) {//返回数据根据结果进行相应的处理
                if (result.code == 200 && result.msg == 1 ) {
                    clearInterval(timer);
                    $('#bindingwx').hide();
                     window.location.reload();
                }

            }
        });
    },2000);
    $('#bindingwx').on('hidden.bs.modal', function (e) {
        clearInterval(timer);
    })
});

$('.unbind_wx_code').on('click',function(){
     var mch_sub_id = $(this).attr('bindvalue');
    //var _this=$(this);
    $('body').ulaiberLoading({loadingText:'确定要解绑吗',loadingType:'comfirm',sureFunction:function(){

        $.ajax(
        {
            type: "get",  //提交方式
            url: sub_user_host + "/merchant/settings/sub_user/bindingstatus",//路径
            data: {
                "mch_sub_id": mch_sub_id,
                "binding": 2
            },//数据，这里使用的是Json格式进行传输
            success: function (result) {
                  if (result.code == 200 && result.msg == 2) {
                      window.location.reload();

            } else {
                      errorTipBtn(result.msg)

            }
            }//返回数据根据结果进行相应的处理
        }
    )
    }});


})













