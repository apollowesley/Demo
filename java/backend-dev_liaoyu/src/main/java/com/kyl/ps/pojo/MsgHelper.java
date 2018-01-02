package com.kyl.ps.pojo;

import java.io.Serializable;

public class MsgHelper implements Serializable {

	private static final long serialVersionUID = 5493936746928733424L;

	public static final Integer SUCCESS_CODE = 0; // 成功码
	public static final Integer ERROR_DATA_CODE = 1; // 数据错误码
	public static final Integer ERROR_AUTH_CODE = 101; // 权限错误

	private Integer status;
	private String message;
	private Object request_date;
	private Object result="";

	


	public Object getRequest_date() {
		return request_date;
	}

	public void setRequest_date(Object request_date) {
		this.request_date = request_date;
	}

	public String getMessage() {
    return message;
  }

  public void setMessage(String message) {
    this.message = message;
  }

  public Integer getStatus() {
		return status;
	}

	public void setStatus(Integer status) {
		this.status = status;
	}

	public Object getResult() {
		return result;
	}

	public void setResult(Object result) {
		this.result = result;
	}

}
