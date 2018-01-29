/**
 * Created by xiezhigang on 16/11/3.
 */

var uuid = "";
var modalStatus=false;
function uploadMchInfo() {
    var excel = $('#xls_file');
    excel.fileinput({
        language: 'zh', //设置语言
        uploadUrl: '/dist/inlet/mch/batch/excel',
        allowedFileExtensions: ['xls', 'xlsx'],//接收的文件后缀
        showUpload: true, //是否显示上传按钮
        showCaption: true,//是否显示标题
        browseClass: "btn btn-primary", //按钮样式
        dropZoneEnabled: true,//是否显示拖拽区域
        maxFileSize: 500,//单位为kb，如果为0表示不限制文件大小
        minFileCount: 0,
        maxFileCount: 1, //表示允许同时上传的最大文件个数
        enctype: 'multipart/form-data',
        validateInitialCount: true,
        previewFileIcon: "<i class='glyphicon glyphicon-king'></i>",
        msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}!"
    }).on("fileuploaded", function (event, data) {
        if (data.response.code == 200) {
            uuid = data.response.uuid;
            if (uuid) {
                $('.modal-body>div:eq(0) .kv-fileinput-error').hide();
                var img = $("#myModalImg");
                var imgHtml = "";
                imgHtml = imgHtml + "<h4 class='modal-title' id='myModal_img'>请选择图片</h4>"
                imgHtml = imgHtml + "<div><input type='file' name='img_file' id='img_file' multiple class='file-loading'/></div>";
                img.html(imgHtml);
                initUploadImg();
            } else {
                $('.modal-body>div:eq(0) .kv-fileinput-error').show().html('请重新上传excel表格')
            }
        } else if( data.response.code == 407){
            $('.modal-body>div:eq(0) .kv-fileinput-error').show().html(data.response.msg);
        } else{
            $('.modal-body>div:eq(0) .kv-fileinput-error').show().html('请重新上传excel表格');
        }
        $('#goNext').hide();
    });
}
function initUploadImg() {
    var image = $('#img_file');
    image.fileinput({
        language: 'zh', //设置语言
        uploadUrl: '/dist/inlet/mch/batch/image?uuid=' + uuid,
        allowedFileExtensions: ['jpg'],//接收的文件后缀
        showUpload: true, //是否显示上传按钮
        showCaption: true,//是否显示标题
        browseClass: "btn btn-primary", //按钮样式
        dropZoneEnabled: true,//是否显示拖拽区域
        maxFileSize: 500,//单位为kb，如果为0表示不限制文件大小
        minFileCount: 3,
        maxFileCount: 50, //表示允许同时上传的最大文件个数
        enctype: 'multipart/form-data',
        validateInitialCount: true,
        previewFileIcon: "<i class='glyphicon glyphicon-king'></i>",
        msgSizeTooLarge: '文件 "{name}" (<b>{size} KB</b>) 允许上传的图片大小为<b>{maxSize} KB</b>.',
        msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}!"
    }).on("fileuploaded", function (event, data) {
        console.log(data);
        if (data.response.code == 200) {
            if (uuid) {
                modalStatus=true;
                $('#myModalImg .kv-fileinput-error').hide();
                document.getElementById('batchMchInlet').action = '/dist/inlet/mch/batch/info?uuid=' + uuid;
                var goNext = $('#goNext');
                var buttonHtml = "";
                buttonHtml = buttonHtml + "<button type='submit' class='btn btn-default' name='next'>下一步</button>";
                goNext.html(buttonHtml);
            } else {
                modalStatus=false;
                $('#myModalImg .kv-fileinput-error').show().html('请先上传excel表格');
            }
        } else if( data.response.code == 407){
            modalStatus=false;
            $('#myModalImg .kv-fileinput-error').show().html(data.response.msg);
        } else {
            modalStatus=false;
            $('#myModalImg .kv-fileinput-error').show().html('上传图片失败');
        }
        if(modalStatus){
            $('#goNext').show();
        }else{
            $('#goNext').hide();
        }
    });
}
uploadMchInfo();
