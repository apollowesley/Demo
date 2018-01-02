package com.kyl.ps.infrastructure.dao;

import java.util.List;
import com.kyl.ps.pojo.BaseInputMessage;


/**
 * 公共数据访问接口, 所有的DAO接口都要继承自该接口
 * <p>Title: BaseSupportDAO.java</p>
 * <p>Description: com.kyl.ps.infrastructure.dao</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2014年11月13日
 *
 */
public interface BaseSupportDAO {

	/**
	 * 
	 * @param <T>
	 * @param obj
	 */
	void insert(Class<? extends Object> clazz, BaseInputMessage inputMessage);
	
	/**
	 * @param <T>
	 * @param obj
	 * @return
	 */
	void update(Class<? extends Object> clazz, BaseInputMessage inputMessage);

	/**
	 * @param <T>
	 * @param clazz
	 * @param parameter
	 * @return
	 */
	void delete(Class<? extends Object> clazz, BaseInputMessage inputMessage);

	/**
	 * 
	 * @param <T>
	 * @param <T>
	 * @param clazz
	 * @param id
	 * @return
	 */
	<T> T selectOne(Class<? extends Object> clazz, BaseInputMessage inputMessage);
	
	/**
	 * @param <T>
	 * @param clazz
	 * @return
	 */
	<T> List<T> selectList(Class<? extends Object> clazz, BaseInputMessage inputMessage);
}
