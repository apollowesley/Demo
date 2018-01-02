package com.kyl.ps.infrastructure.dao.impl.collect;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Repository;

import com.kyl.ps.infrastructure.dao.MDSSupportCommonDAOImpl;
import com.kyl.ps.infrastructure.dao.Namingspace;
import com.kyl.ps.pojo.BaseInputMessage;

/**
 * 垃圾回收管理 操作
 * 
 * @author xiao.liao
 *
 */
@Repository
@Namingspace("collect")
public class CollectDao extends MDSSupportCommonDAOImpl {
	
	
	
	// 查询某贴纸的厨余记录
	public List<Map<String, Object>> queryKitchenBySid(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "queryKitchenBySid"),
				inputMessage.getRequestMap());
	}
	public int queryKitchenBySidCount(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "queryKitchenBySidCount"),
				inputMessage.getRequestMap());
	}
	
	
	// 查询某贴纸的小件投递记录
	public List<Map<String, Object>> queryGarbageBySid(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "queryGarbageBySid"),
				inputMessage.getRequestMap());
	}
	public int queryGarbageBySidCount(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "queryGarbageBySidCount"),
				inputMessage.getRequestMap());
	}
	
}
