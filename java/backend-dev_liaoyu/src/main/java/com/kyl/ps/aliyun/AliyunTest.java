package com.kyl.ps.aliyun;

import com.aliyun.oss.OSSClient;

import java.io.File;

/**
 * Created by Administrator on 2017/2/21 0021.
 */
public class AliyunTest {

//    // endpoint以杭州为例，其它region请按实际情况填写
//    String endpoint = "http://oss-cn-hangzhou.aliyuncs.com";
//    // accessKey请登录https://ak-console.aliyun.com/#/查看
//    String accessKeyId = "<yourAccessKeyId>";
//    String accessKeySecret = "<yourAccessKeySecret>";
//    // 创建OSSClient实例
//    OSSClient ossClient = new OSSClient(endpoint, accessKeyId, accessKeySecret);
//    // 设置断点续传请求
//    UploadFileRequest uploadFileRequest = new UploadFileRequest("<yourBucketName>", "<yourKey>");
//    // 指定上传的本地文件
//    uploadFileRequest.setUploadFile("<yourLocalFile>");
//    // 指定上传并发线程数
//    uploadFileRequest.setTaskNum(5);
//    // 指定上传的分片大小
//    uploadFileRequest.setPartSize(1 * 1024 * 1024);
//    // 开启断点续传
//    uploadFileRequest.setEnableCheckpoint(true);
//    // 断点续传上传
//    ossClient.uploadFile(uploadFileRequest);
//    // 关闭client
//    ossClient.shutdown();
    public  static void main(String sd[]){
        // endpoint以杭州为例，其它region请按实际情况填写
        String endpoint = "oss-cn-shenzhen.aliyuncs.com";
        // accessKey请登录https://ak-console.aliyun.com/#/查看
                String accessKeyId = "LTAIKm16SvdURolO";
                String accessKeySecret = "45cEC00EZjl8t6azSmrBOpj1RDIu1o";
        // 创建OSSClient实例
                OSSClient ossClient = new OSSClient(endpoint, accessKeyId, accessKeySecret);
//        // 上传文件
//                ossClient.putObject("diu-news-images", "tqTTT_diudiuUse1.png", new File("d:/3eb9261f-d7c2-4bc2-a422-e528088ff574.png"));
//        // 关闭client
//            ossClient.shutdown();
//            System.out.println("====上传成功=====");

    // 删除Object
            ossClient.deleteObject("diu-news-images", "tqTTT_diudiuUse1.png");
    // 关闭client
            ossClient.shutdown();
    }
}
