package com.kyl.ps.infrastructure.dao.impl.account;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Repository;

import com.kyl.ps.infrastructure.dao.MDSSupportCommonDAOImpl;
import com.kyl.ps.infrastructure.dao.Namingspace;
import com.kyl.ps.model.manageruser.ManagerUser;
import com.kyl.ps.pojo.BaseInputMessage;

/**
 * <p>Title: UserDao.java</p>
 * <p>Description: com.kyl.ps.infrastructure.dao.impl</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2015年1月4日
 *
 */
@Repository
@Namingspace("manageruser")
public class ManagerUserDao extends MDSSupportCommonDAOImpl{
	private String pcsParameters(String[] query){
		String q = new String();
		for (int i = 0; i < query.length; i++) {
			q+="_"+query[i]; 
		}
		
		return q;
	}
	public ManagerUser selectOne(Class<? extends Object>  clazz,BaseInputMessage inputMessage,String ...query){
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "selectOne"+pcsParameters(query)), inputMessage.getRequestMap());
	}
	
	
	public void delete(Class<? extends Object>  clazz,BaseInputMessage inputMessage,String ...query){
		sqlSessionTemplate.delete(warpSqlstatement(clazz, "delete"+pcsParameters(query)), inputMessage.getRequestMap());
	}
	
	
	public void insert(Class<? extends Object>  clazz,BaseInputMessage inputMessage,String ...query){
		sqlSessionTemplate.insert(warpSqlstatement(clazz, "insert"+pcsParameters(query)), inputMessage.getRequestMap());
	}
	
	
	public List<Map<String,Object>> queryAllManagerUser(Class<? extends Object>  clazz,BaseInputMessage inputMessage){
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "queryAllManagerUser"), inputMessage.getRequestMap());
	}
	
	public Map<String,Object> queryManagerUser(Class<? extends Object>  clazz,BaseInputMessage inputMessage){
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "queryManagerUser"), inputMessage.getRequestMap());
	}
	
	
	public void updateOmsAccount(Class<? extends Object>  clazz,BaseInputMessage inputMessage){
		 sqlSessionTemplate.update(warpSqlstatement(clazz, "updateOmsAccount"), inputMessage.getRequestMap());
	}


	public  List<Map<String,Object>> queryAllMenu(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "queryAllMenu"), inputMessage.getRequestMap());
	}

	public List<Map<String,Object>> queryUserRoleMenu(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "queryUserRoleMenu"), inputMessage.getRequestMap());
	}

	public List<Map<String,Object>>  getUserRoleMenuList(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getUserRoleMenuList"), inputMessage.getRequestMap());
	}

	public int deleteRoleMenu(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.delete(warpSqlstatement(clazz, "deleteRoleMenu"), inputMessage.getRequestMap());
	}

	public int saveRoleMenu(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.insert(warpSqlstatement(clazz, "saveRoleMenu"), inputMessage.getRequestMap());
	}

	public List<Map<String,Object>> getRoleList(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getRoleList"));
	}

    public List<Map<String,Object>> getUserListByRoleId(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getUserListByRoleId"), inputMessage.getRequestMap());
    }

	public List<Map<String,Object>> getUserModuleByUserId(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getUserModuleByUserId"), inputMessage.getRequestMap());
	}

	public int deleteUserModule(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.delete(warpSqlstatement(clazz, "deleteUserModule"), inputMessage.getRequestMap());
	}

	public int saveUserModule(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.insert(warpSqlstatement(clazz, "saveUserModule"), inputMessage.getRequestMap());
	}

	public int addRole(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.insert(warpSqlstatement(clazz, "addRole"), inMessage.getRequestMap());
	}

	public int createUser(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.insert(warpSqlstatement(clazz, "createUser"), inMessage.getRequestMap());
	}

	public int resetPassword(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.update(warpSqlstatement(clazz, "resetPassword"), inMessage.getRequestMap());
	}

	public Map<String,Object> queryManagerUserByUserId(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "queryManagerUserByUserId"), inMessage.getRequestMap());
	}

    public List<Map<String,Object>> getAllUserInfoList(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getAllUserInfoList"), inMessage.getRequestMap());
    }

	public Map<String,Object> getAllUserInfoListCount(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "getAllUserInfoListCount"), inMessage.getRequestMap());
	}
}
