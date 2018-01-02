package com.kyl.ps.model.config;

import java.io.Serializable;

/**
 * <p>Title: CustomMenuChild.java</p>
 * <p>Description: com.kyl.ps.model.config</p>
 * <p>Copyright: Copyright (c) 2015</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2015年1月6日
 *
 */
public class CustomMenuChild implements Serializable{

	/**
	 * 
	 */
	private static final long serialVersionUID = -3022257574625264568L;

	private String dateStr;

	public String getDateStr() {
		return dateStr;
	}

	public void setDateStr(String dateStr) {
		this.dateStr = dateStr;
	}

}
