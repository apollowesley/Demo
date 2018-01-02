package com.kyl.ps.pojo;

import java.util.HashMap;
import java.util.Map;

public class BaseInputMessage {
	@SuppressWarnings("rawtypes")
	Map requestMap = new HashMap();

	@SuppressWarnings("rawtypes")
	public Map getRequestMap() {
		return requestMap;
	}

	@SuppressWarnings("rawtypes")
	public void setRequestMap(Map requestMap) {
		this.requestMap = requestMap;
	}
	
}
