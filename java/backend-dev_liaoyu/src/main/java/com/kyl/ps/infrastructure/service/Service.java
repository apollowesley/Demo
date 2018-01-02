package com.kyl.ps.infrastructure.service;

/**
 * 
 * <p>Title: Service</p>
 * <p>Description: com.soarsky.ps.service.system</p>
 * <p>Copyright: Copyright (c) 2013</p>
 * <p>Company: Kyn</p>
 * @author    Jason.Guo
 * @date      2013-3-2
 */
public interface Service extends Runnable {

	   /**
	    * 这个方法是必须被实现的  
	    * @param baseMessage
	    * @return
	 * @throws Exception 
	    */
	void invoke() throws Exception;

}
