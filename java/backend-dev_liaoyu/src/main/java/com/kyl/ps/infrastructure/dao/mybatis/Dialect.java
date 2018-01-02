package com.kyl.ps.infrastructure.dao.mybatis;

/**
 * 
 * <p>Title: Dialect.java</p>
 * <p>Description: com.kyl.ps.infrastructure.dao.mybatis</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2014年11月21日
 *
 */
public abstract class Dialect {

	public static enum Type{
		MYSQL,
		ORACLE
	}
	
	public abstract String getLimitString(String sql, int skipResults, int maxResults);
	
}