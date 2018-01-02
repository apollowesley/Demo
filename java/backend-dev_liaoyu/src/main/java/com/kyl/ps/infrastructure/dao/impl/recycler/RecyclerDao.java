package com.kyl.ps.infrastructure.dao.impl.recycler;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Repository;

import com.kyl.ps.infrastructure.dao.MDSSupportCommonDAOImpl;
import com.kyl.ps.infrastructure.dao.Namingspace;
import com.kyl.ps.pojo.BaseInputMessage;

/**
 * 回收人员dao
 * 
 * @author xiao.liao
 *
 */
@Repository
@Namingspace("recycle")
public class RecyclerDao extends MDSSupportCommonDAOImpl {
	public void insertRecycler(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		sqlSessionTemplate.insert(warpSqlstatement(clazz, "insertRecycler"),
				inputMessage.getRequestMap());
	}
	
	public void editRecycler(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		sqlSessionTemplate.update(warpSqlstatement(clazz, "editRecycler"),
				inputMessage.getRequestMap());
	}
	
	
	public List<Map<String, Object>> queryRecycles(Class<? extends Object> clazz,
			BaseInputMessage inputMessage){
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "queryRecycles"),
				inputMessage.getRequestMap());
	}
	public List<Map<String, Object>> queryAllRecycles(Class<? extends Object> clazz,
			BaseInputMessage inputMessage){
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "queryAllRecycles"),
				inputMessage.getRequestMap());
	}
	public int queryRecyclesCount(Class<? extends Object> clazz,
			BaseInputMessage inputMessage){
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "queryRecyclesCount"),
				inputMessage.getRequestMap());
	}
}
