package com.kyl.ps.infrastructure.service;

import com.kyl.ps.pojo.BaseInputMessage;
import com.kyl.ps.pojo.BaseReturnMessage;


/**
 * 
 * <p>Title: AbstractService</p>
 * <p>Description: com.kyn.ps.kyn.system</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyn</p>
 * @author    Jason.Guo
 * @date      2014-10-10
 */
public abstract class AbstractService implements Service {
	
	//输入参数
	protected BaseInputMessage inputMessage=new BaseInputMessage();
	
	//数据库的返回
	protected BaseReturnMessage returnMessage= new  BaseReturnMessage();
	
    //准备数据  做执行数据库之前做一些准备工作
	protected   abstract  void beforeInvoke() throws Exception ;

	//执行数据库操作
    public abstract void invoke() throws Exception ;
	
	//对数据库返回的数据做一些操作
	protected  abstract void afterInvoke() throws Exception;
	
    public void run() {}

	public  BaseReturnMessage   proess(BaseInputMessage inMessage)  throws Exception
	{
		inputMessage=inMessage;
		
		
			beforeInvoke();
			invoke();
			afterInvoke();
			
	
		return returnMessage;
		
	}

	public void setReturnMessage(BaseReturnMessage returnMessage) {
		this.returnMessage = returnMessage;
	}

	public void setInputMessage(BaseInputMessage inputMessage) {
		this.inputMessage = inputMessage;
	}


}
