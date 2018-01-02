package com.kyl.ps.pojo;

import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;

import net.sf.json.JSONObject;

import com.kyl.ps.util.DateUtils;
//import com.kyl.ps.util.JsonConvertor;


/**
 * <p>Title: BaseMessage</p>
 * <p>Description: com.soarsky.ps.pojo.bo</p>
 * <p>Copyright: Copyright (c) 2013</p>
 * <p>Company: Act</p>

 */
public class BaseReturnMessage implements Serializable {

    //	/** serialVersionUID */
    //	private static final long serialVersionUID = 4139274922395439481L;

    /** serialVersionUID*/
    private static final long serialVersionUID = 4054203600832904880L;
    private Object result; // 用于存放每次结果的对象
    private String resultStr; // 用于存放每次结果的json string
    private String resultKey; // 用于存放每次结果的key
    
    @SuppressWarnings("rawtypes")
	private Map resultsMap = new HashMap(); // 用于存放多个结果集 key value

    private String code;
    private String detail;



	public void createErrorResult() throws Exception {
  
        ResultObject resultObject = new ResultObject();
        resultObject.setIs_success(false);
        resultObject.setTimestamp(String.valueOf(DateUtils.getCurrentTimeStemp()));
        resultObject.setCode(getCode());
        resultObject.setDetail(getDetail());
        this.setResult(resultObject);
        //JsonConvertor.object2Str(this);
        JSONObject.fromObject(this);
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
    

	public Object getResult() {
		return result;
	}
	public void setResult(Object result) {
		this.result = result;
	}
	public String getResultStr() {
		return resultStr;
	}
	public void setResultStr(String resultStr) {
		this.resultStr = resultStr;
	}
	public String getResultKey() {
		return resultKey;
	}
	public void setResultKey(String resultKey) {
		this.resultKey = resultKey;
	}
	
	@SuppressWarnings("rawtypes")
	public Map getResultsMap() {
		return resultsMap;
	}
	
	@SuppressWarnings("rawtypes")
	public void setResultsMap(Map resultsMap) {
		this.resultsMap = resultsMap;
	}
}
