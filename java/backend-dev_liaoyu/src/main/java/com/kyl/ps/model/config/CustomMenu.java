package com.kyl.ps.model.config;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

/**
 * <p>Title: CustomMenu.java</p>
 * <p>Description: com.kyl.ps.model.config</p>
 * <p>Copyright: Copyright (c) 2015</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2015年1月6日
 *
 */
public class CustomMenu implements Serializable{

	/**
	 * 
	 */
	private static final long serialVersionUID = 7819965272094709044L;

	private String tag;
	
	private List<CustomMenuChild> menuChilds = new ArrayList<CustomMenuChild>();

	public String getTag() {
		return tag;
	}

	public void setTag(String tag) {
		this.tag = tag;
	}

	public List<CustomMenuChild> getMenuChilds() {
		return menuChilds;
	}

	public void setMenuChilds(List<CustomMenuChild> menuChilds) {
		this.menuChilds = menuChilds;
	}
}
