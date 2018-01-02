package com.kyl.ps.constant;

/**
 * Created by zxd on 2017/2/6 0006.
 */

/**
 * Created by zxd on 2016/10/18.
 */
public enum ResponseStatus {
    SUCCESS(0                                      ,"成功"),
    NOTPEPERMISSION(2102                          ,"用户没有任何权限"),
    NAMEALREADYEXISTS(2103                        ,"名称已存在"),
    SERVERERROR(500                                ,"服务器异常"),;
    private  int  statusCode;//错误码
    private  String statusName;//状态名
    private  ResponseStatus(int statusCode,String statusName){
        this.statusCode  = statusCode;
        this.statusName  = statusName;
    }

    public int getStatusCode() {
        return statusCode;
    }

    public void setStatusCode(int statusCode) {
        this.statusCode = statusCode;
    }

    public String getStatusName() {
        return statusName;
    }

    public void setStatusName(String statusName) {
        this.statusName = statusName;
    }
}
