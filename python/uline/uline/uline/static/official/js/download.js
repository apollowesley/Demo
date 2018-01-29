$().ready(function () {
    //头部下载
    //$("#download").popover({trigger: 'hover', placement: 'bottom', content: "导出数据超过1000条,正在后台生成报表,稍后可以在这里下载"});

});

function downloadExportFile(order_id) {
    $.ajax({
        type: 'GET',
        data: {"order_id": order_id},
        dataType: 'json',
        url: '/official/utils/download/export',
        beforeSend: function (XMLHttpRequest) {
        },
        success: function (res) {
            if (res.code == 200) {
                location.href = res.data
            } else {
                alert(res.msg)
            }
        },
        complete: function (XMLHttpRequest, textStatus) {
        },
        error: function (xhr) {
        }
    });
    return false;
}

function deleteExportFile(order_id) {
    //获取id
    var deleteId = "#tr_" + order_id;
    $.ajax({
        type: 'GET',
        data: {"order_id": order_id},
        dataType: 'json',
        url: '/official/utils/download/delete',
        beforeSend: function (XMLHttpRequest) {
        },
        success: function (res) {
            if (res.code == 200) {
                $("body").append("<div class='newSuccess'>删除成功</div>");
                $(".newSuccess").delay(1000).fadeOut(2000);

                //删除
                $(deleteId).parent().parent().remove();
            } else {
                alert(res.msg)
                //删除
                $(deleteId).parent().parent().remove();
            }
        },
        complete: function (XMLHttpRequest, textStatus) {
        },
        error: function (xhr) {
        }
    });
    return false;
}


  