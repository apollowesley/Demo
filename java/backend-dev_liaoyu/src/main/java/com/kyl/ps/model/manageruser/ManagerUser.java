package com.kyl.ps.model.manageruser;

import java.io.Serializable;

/**
 * <p>Title: User.java</p>
 * <p>Description: com.kyl.ps.model</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2015年1月4日
 *
 */
public class ManagerUser implements Serializable{

	/**
	 * 
	 */
	private static final long serialVersionUID = 5837214065103064604L;
	
	private String id;
	
	private String userName;
	
	private String password;
	
	private String dept;
	
	private String status;
			
	private String createTime;
	
	private String roleId;
	
	
	
	
	
	
	private int keyId;
	private int accountId;
	private int rolls;
	private int rollsQuantity;
	private String prefix;
	private String expirationTime;
	private String name;
	
	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public int getKeyId() {
		return keyId;
	}

	public void setKeyId(int keyId) {
		this.keyId = keyId;
	}

	public int getAccountId() {
		return accountId;
	}

	public void setAccountId(int accountId) {
		this.accountId = accountId;
	}

	public int getRolls() {
		return rolls;
	}

	public void setRolls(int rolls) {
		this.rolls = rolls;
	}

	public int getRollsQuantity() {
		return rollsQuantity;
	}

	public void setRollsQuantity(int rollsQuantity) {
		this.rollsQuantity = rollsQuantity;
	}

	public String getPrefix() {
		return prefix;
	}

	public void setPrefix(String prefix) {
		this.prefix = prefix;
	}

	public String getExpirationTime() {
		return expirationTime;
	}

	public void setExpirationTime(String expirationTime) {
		this.expirationTime = expirationTime;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getUserName() {
		return userName;
	}

	public void setUserName(String userName) {
		this.userName = userName;
	}

	public String getPassword() {
		return password;
	}

	public void setPassword(String password) {
		this.password = password;
	}

	public String getDept() {
		return dept;
	}

	public void setDept(String dept) {
		this.dept = dept;
	}

	public String getStatus() {
		return status;
	}

	public void setStatus(String status) {
		this.status = status;
	}

	public String getCreateTime() {
		return createTime;
	}

	public void setCreateTime(String createTime) {
		this.createTime = createTime;
	}

	public String getRoleId() {
		return roleId;
	}

	public void setRoleId(String roleId) {
		this.roleId = roleId;
	}


}
