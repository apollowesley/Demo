package com.kyl.ps.infrastructure.dao.impl.dict;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Repository;

import com.kyl.ps.infrastructure.dao.MDSSupportCommonDAOImpl;
import com.kyl.ps.infrastructure.dao.Namingspace;
import com.kyl.ps.pojo.BaseInputMessage;

/**
 * 小区信息dao
 * 
 * @author xiao.liao
 *
 */
@Repository
@Namingspace("dict")
public class DictDao extends MDSSupportCommonDAOImpl {
	
	
	public List<Map<String, Object>> queryGaedens(Class<? extends Object> clazz,
			BaseInputMessage inputMessage){
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "queryGaedens"),
				inputMessage.getRequestMap());
	}
}
