package com.kyl.ps.model.account;

import java.io.Serializable;
import java.util.List;

/**
 * 角色实体类
 * <p>Title: Role.java</p>
 * <p>Description: com.kyl.ps.model.account</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: Bo.Wang
 * @date:   2015年1月23日
 *
 */
public class Role implements Serializable{

	private static final long serialVersionUID = 4799759884941466820L;
	
	/**
	 * id
	 */
	private String id;	
	
	/**
	 * 角色名称
	 */
	private String roleName;	
	
	/**
	 * 显示状态
	 */
	private String showFlag;	
	
	/**
	 * 创建时间
	 */
	private String createTime;	
	
	/**
	 * 该角色拥有的权限
	 */
	private List<String> permission;
	
	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public String getRoleName() {
		return roleName;
	}

	public void setRoleName(String roleName) {
		this.roleName = roleName;
	}

	public String getShowFlag() {
		return showFlag;
	}

	public void setShowFlag(String showFlag) {
		this.showFlag = showFlag;
	}

	public String getCreateTime() {
		return createTime;
	}

	public void setCreateTime(String createTime) {
		this.createTime = createTime;
	}

	public List<String> getPermission() {
		return permission;
	}

	public void setPermission(List<String> permission) {
		this.permission = permission;
	}
	
}
