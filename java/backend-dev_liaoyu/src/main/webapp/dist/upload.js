var myUploader = (function(){
    
    var imgData = {

        accessId:'LTAIKm16SvdURolO',
        accesskey:'45cEC00EZjl8t6azSmrBOpj1RDIu1o',
        host:'http://diu-news-images.oss-cn-shenzhen.aliyuncs.com/'
    };

    var policyText = {
        "expiration": "2020-01-01T12:00:00.000Z", //设置该Policy的失效时间，超过这个失效时间之后，就没有办法通过这个policy上传文件了
        "conditions": [
        ["content-length-range", 0, 1048576000] // 设置上传文件的大小限制
        ]
    };

    var policyBase64 = Base64.encode(JSON.stringify(policyText))
    var bytes = Crypto.HMAC(Crypto.SHA1, policyBase64, imgData.accesskey, { asBytes: true }) ;
    var signature = Crypto.util.bytesToBase64(bytes);

    var preStr = "upload/";
  
    function setPreStr(value){
        preStr  = value;
    }

    function set_upload_param(up, filename, file)
    {
        var strAry = filename.split(".");
        var new_multipart_params = {
            'key' : preStr + md5(strAry[0]) + "." + strAry[1],
            'policy': policyBase64,
            'OSSAccessKeyId': imgData.accessId, 
            'success_action_status' : '200', //让服务端返回200,不然，默认会返回204
            'signature': signature,
        };

        if(file) {
            file.tempKey = new_multipart_params.key;
        }

        up.setOption({
            'url': imgData.host,
            'multipart_params': new_multipart_params
        });

        up.start();
    }

    var uploader;
    var changeFunc;
    var callFunc;

    function init(changeCallBack,callBack){
       if(uploader){
            return;
       }
       changeFunc = changeCallBack;
       callFunc = callBack;
       uploader = new plupload.Uploader({
            runtimes : 'html5,flash,silverlight,html4',
            browse_button : 'selectfiles', 
            //multi_selection: false,
            container: document.getElementById('imgUpContainer'),
            flash_swf_url : 'lib/plupload-2.1.2/js/Moxie.swf',
            silverlight_xap_url : 'lib/plupload-2.1.2/js/Moxie.xap',
            url : 'http://oss.aliyuncs.com',

            init: {
               
                FilesAdded: function(up, files) {
                    
                    if(changeFunc){
                        changeFunc();
                    }

                    setTimeout(()=>{

                        plupload.each(files, function(file) {
                            document.getElementById('ossfile').innerHTML += '<div id="' + file.id + '">' + file.name + ' (' + plupload.formatSize(file.size) + ')<b></b>'
                            +'<div class="progress"><div class="progress-bar" style="width: 0%"></div></div>'
                            +'</div>';
                        });

                        set_upload_param(uploader, "", false);
                    },500);
                },
                BeforeUpload: function(up, file) {
                    set_upload_param(up, file.name, file);
                },

                UploadProgress: function(up, file) {
                    var d = document.getElementById(file.id);
                    d.getElementsByTagName('b')[0].innerHTML = '<span>' + file.percent + "%</span>";
                    var prog = d.getElementsByTagName('div')[0];
                    var progBar = prog.getElementsByTagName('div')[0]
                    progBar.style.width =  4*file.percent+'px';
                    progBar.setAttribute('aria-valuenow', file.percent);
                },

                FileUploaded: function(up, file, info) {
                  // console.log(111);
                },

                UploadComplete:function(up,files){
                    if(callFunc){
                        callFunc(files);
                    }

                    up.splice(0);
                },

                Error: function(up, err) {
                    // document.getElementById('console').appendChild(document.createTextNode("\nError xml:" + err.response));
                }
            }
        });

        uploader.init();
    }

    return {init,setPreStr};
})();