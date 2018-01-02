package com.kyl.ps.infrastructure.dao.mybatis;

/**
 * 包装mysql分页查询
 * <p>Title: MySqlDialect.java</p>
 * <p>Description: com.kyl.ps.infrastructure.dao.mybatis</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2014年11月21日
 *
 */
public class MySqlDialect extends Dialect{

	/* (non-Javadoc)
	 * @see org.mybatis.extend.interceptor.IDialect#getLimitString(java.lang.String, int, int)
	 */
	@Override
	public String getLimitString(String sql, int offset, int limit) {

		sql = sql.trim();
		StringBuffer pagingSelect = new StringBuffer(sql.length() + 10);
		pagingSelect.append(sql+" limit "+offset+","+limit);
		return pagingSelect.toString();
	}

}