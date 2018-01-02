package com.kyl.ps.infrastructure.dao;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.annotation.Resource;

import org.apache.ibatis.session.RowBounds;
import org.mybatis.spring.SqlSessionTemplate;

import com.kyl.ps.infrastructure.dao.mybatis.Page;
import com.kyl.ps.pojo.BaseInputMessage;

/**
 * <p>Title: MDSSupportCommonDAOImpl.java</p>
 * <p>Description: com.kyl.ps.infrastructure.dao.impl</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2014年11月13日
 *
 */
public abstract class MDSSupportCommonDAOImpl implements BaseSupportDAO{
	
	/**
	 * 命名空间与SQL语句分隔符号
	 */
	public static final String _SQL_SEP = "_";

	/**
	 * 命名映射
	 */
	public static final Map<String, String> namingMap = new HashMap<String, String>();
	
	/**
	 * 通用INSERT语句
	 */
	public static final String _SQL_INSERT = "insert";
	
	/**
	 * 通用UPDATE语句
	 */
	public static final String _SQL_UPDATE = "update";
	
	/**
	 * 通用DELETE语句
	 */
	public static final String _SQL_DELETE = "delete";
	
	public SqlSessionTemplate getSqlSessionTemplate() {
		return sqlSessionTemplate;
	}

	public void setSqlSessionTemplate(SqlSessionTemplate sqlSessionTemplate) {
		this.sqlSessionTemplate = sqlSessionTemplate;
	}

	/**
	 * 通用SELECT ONE语句
	 */
	public static final String _SQL_SELECTONE = "selectOne";
	
	/**
	 * 通用SELECT LIST语句
	 */
	public static final String _SQL_SELECTLIST = "selectList";

	@Resource(name="sqlSessionTemplate")
	protected SqlSessionTemplate sqlSessionTemplate;


	/*
	 * (non-Javadoc)
	 * @see com.kyl.ps.infrastructure.dao.BaseSupportDAO#insert(java.lang.Class, com.kyl.ps.pojo.BaseInputMessage)
	 */
	public void insert(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		 sqlSessionTemplate.insert(warpSqlstatement(clazz, _SQL_INSERT), inputMessage.getRequestMap());
	}
	
	/*
	 * (non-Javadoc)
	 * @see com.kyl.ps.infrastructure.dao.BaseSupportDAO#update(java.lang.Class, com.kyl.ps.pojo.BaseInputMessage)
	 */
	public void update(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		 sqlSessionTemplate.update(warpSqlstatement(clazz, _SQL_UPDATE), inputMessage.getRequestMap());
		
		
	}
	
	/*
	 * (non-Javadoc)
	 * @see com.kyl.ps.infrastructure.dao.BaseSupportDAO#delete(java.lang.Class, com.kyl.ps.pojo.BaseInputMessage)
	 */
	public void delete(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		 sqlSessionTemplate.delete(warpSqlstatement(clazz, _SQL_DELETE), inputMessage.getRequestMap());
	}
	
	
	/*
	 * (non-Javadoc)
	 * @see com.kyl.ps.infrastructure.dao.BaseSupportDAO#selectList(java.lang.Class, com.kyl.ps.pojo.BaseInputMessage)
	 */
	public <T> List<T> selectList(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return  sqlSessionTemplate.selectList(warpSqlstatement(clazz, _SQL_SELECTLIST), inputMessage.getRequestMap());
	}
	
	
	public <T>  T selectOne(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return  sqlSessionTemplate.selectOne(warpSqlstatement(clazz, _SQL_SELECTLIST), inputMessage.getRequestMap());
	}
	/**
	 * 获取命名空间名称
	 * @param clazz
	 * @param stmt    
	 * @return
	 */
	protected String warpSqlstatement(Class<? extends Object> clazz, String stmt){
		final String namespace = this.getNamesapce(clazz);
		return namespace + _SQL_SEP + stmt;
	}
	
	/**
	 * 获取命名空间名称
	 * @param clazz    对象类型
	 * @return
	 */
	protected String getNamesapce(Class<? extends Object> clazz){
		String namespace = null;
		final String clazzName = clazz.getName();
		
		// 从缓存中获取
		namespace = namingMap.get(clazzName);
		
		// 如果缓存中还没有保存对应的SQL命名空间名称，则初始化并且加载
		if(null == namespace){
			Namingspace _namespace = (Namingspace)clazz.getAnnotation(Namingspace.class);
			namespace = _namespace.value();
			if(null == namespace || "".equals(namespace.trim())){
				throw new RuntimeException ("namespace is empty.");
			}
			namingMap.put(clazzName, namespace);
		}
		return namespace;
	}
	
	/**
	 * 
	 * 分页查询
	 *
	 * @Author: xiaoliao
	 * 
	 * @param statement SQL语句别名
	 * @param params 查询参数
	 * @return
	 */
	@SuppressWarnings("rawtypes")
	public Page queryPageList(Class<? extends Object> clazz, String statement, BaseInputMessage inputMessage) {

		int offset = Integer.parseInt(inputMessage.getRequestMap().get("mr")
				.toString())
				* (Integer.parseInt(inputMessage.getRequestMap().get("start")
						.toString()) - 1);
		List list = this.sqlSessionTemplate.selectList(
				warpSqlstatement(clazz, statement),
				inputMessage.getRequestMap(),
				new RowBounds(offset, Integer.parseInt(inputMessage
						.getRequestMap().get("mr").toString())));
		String warpsql = warpSqlstatement(clazz, statement) + "Count";
		int total = (Integer) this.sqlSessionTemplate.selectOne(warpsql,inputMessage.getRequestMap());
		Page page = new Page(list, offset, total, Integer.parseInt(inputMessage
				.getRequestMap().get("mr").toString()));
		return page;
	}
	
}
