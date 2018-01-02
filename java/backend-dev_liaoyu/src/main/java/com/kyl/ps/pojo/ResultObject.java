package com.kyl.ps.pojo;

/**
 * 
 * <p>Title: ResultObject</p>
 * <p>Description: com.soarsky.ps.pojo.bo</p>
 * <p>Copyright: Copyright (c) 2013</p>
 * <p>Company: kyn</p>
 * @author    Jason.Guo
 * @date      2014-10-10
 */
public class ResultObject {

    private boolean is_success = true;
    private String timestamp = "";
    private Object body;
    private String code = "";
    private String detail = "";

    public boolean isIs_success() {
        return is_success;
    }

    public void setIs_success(boolean is_success) {
        this.is_success = is_success;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }

    public Object getBody() {
        return body;
    }

    public void setBody(Object body) {
        this.body = body;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getDetail() {
        return detail;
    }

    public void setDetail(String detail) {
        this.detail = detail;
    }

}
