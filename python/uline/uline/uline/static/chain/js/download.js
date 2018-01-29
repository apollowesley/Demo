$().ready(function () {
    //头部下载
    //$("#download").popover({trigger: 'hover', placement: 'bottom', content: "导出数据超过1000条,正在后台生成报表,稍后可以在这里下载"});

});

function downloadExportFile(order_id) {
    $.ajax({
        type: 'GET',
        data: {"order_id": order_id},
        dataType: 'json',
        url: '/chain/utils/download/export',
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
    $.ajax({
        type: 'GET',
        data: {"order_id": order_id},
        dataType: 'json',
        url: '/chain/utils/download/delete',
        beforeSend: function (XMLHttpRequest) {
        },
        success: function (res) {
            if (res.code == 200) {
                alert('删除成功');
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


  