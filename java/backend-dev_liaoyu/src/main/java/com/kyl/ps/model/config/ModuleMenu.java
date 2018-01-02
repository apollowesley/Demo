package com.kyl.ps.model.config;

import java.io.Serializable;
import java.util.List;

/**
 * <p>Title: ModuleMenu.java</p>
 * <p>Description: com.kyl.ps.model.config</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2015年1月5日
 *
 */
public class ModuleMenu implements Serializable{

	/**
	 * 
	 */
	private static final long serialVersionUID = -8824437867124744834L;
	
    private String id;
    
    private String moduleId; //0表示为一级菜单
	
	private String menuName;
	
	private String menuUrl;

	private List<ModuleMenu> menus;
	
	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public String getModuleId() {
		return moduleId;
	}

	public void setModuleId(String moduleId) {
		this.moduleId = moduleId;
	}

	public String getMenuName() {
		return menuName;
	}

	public void setMenuName(String menuName) {
		this.menuName = menuName;
	}

	public String getMenuUrl() {
		return menuUrl;
	}

	public void setMenuUrl(String menuUrl) {
		this.menuUrl = menuUrl;
	}

	public List<ModuleMenu> getMenus() {
		return menus;
	}

	public void setMenus(List<ModuleMenu> menus) {
		this.menus = menus;
	}

	
}
