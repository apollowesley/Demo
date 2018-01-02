package com.kyl.ps.infrastructure.dao.impl.customer;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Repository;

import com.kyl.ps.infrastructure.dao.MDSSupportCommonDAOImpl;
import com.kyl.ps.infrastructure.dao.Namingspace;
import com.kyl.ps.pojo.BaseInputMessage;

/**
 * 用户dao
 * 
 * @author xiao.liao
 *
 */
@Repository
@Namingspace("customer")
public class CustomerDao extends MDSSupportCommonDAOImpl {
	public void insertCustomer(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		sqlSessionTemplate.insert(warpSqlstatement(clazz, "insertCustomer"),
				inputMessage.getRequestMap());
	}
	public void updateUserMobileById(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		sqlSessionTemplate.update(warpSqlstatement(clazz, "updateUserMobileById"),
				inputMessage.getRequestMap());
	}
	
	
	public Map<String, Object> queryCustomerInfo(Class<? extends Object> clazz,
			BaseInputMessage inputMessage){
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "queryCustomerInfo"),
				inputMessage.getRequestMap());
	}
	public Map<String, Object> queryUserMobileById(Class<? extends Object> clazz,
			BaseInputMessage inputMessage){
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "queryUserMobileById"),
				inputMessage.getRequestMap());
	}
	public int queryUsagerecordCount(Class<? extends Object> clazz,
			BaseInputMessage inputMessage){
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "queryUsagerecordCount"),
				inputMessage.getRequestMap());
	}
	
	
	public List<Map<String, Object>> queryUsagerecord(Class<? extends Object> clazz,
			BaseInputMessage inputMessage){
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "queryUsagerecord"),
				inputMessage.getRequestMap());
	}
	public List<Map<String, Object>> queryAllUser(Class<? extends Object> clazz,
			BaseInputMessage inputMessage){
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "queryAllUser"),
				inputMessage.getRequestMap());
	}
	public List<Map<String, Object>> queryAllUserExtend(Class<? extends Object> clazz,
			BaseInputMessage inputMessage){
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "queryAllUserExtend"),
				inputMessage.getRequestMap());
	}
}
