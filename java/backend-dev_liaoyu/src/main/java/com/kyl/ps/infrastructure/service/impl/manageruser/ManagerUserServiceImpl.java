package com.kyl.ps.infrastructure.service.impl.manageruser;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.kyl.ps.infrastructure.dao.impl.account.ManagerUserDao;
import com.kyl.ps.infrastructure.service.AbstractService;
import com.kyl.ps.pojo.BaseInputMessage;

/**
 * <p>Title: UserLoginServiceImpl.java</p>
 * <p>Description: com.kyl.ps.infrastructure.service.impl</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2015年1月5日
 *
 */
@Service
public class ManagerUserServiceImpl extends AbstractService{

	@Autowired
     ManagerUserDao managerUserDao;
	
	
	
	@Override
	protected void beforeInvoke() throws Exception {
		
	}

	@Override
	public void invoke() throws Exception {
	}

	@Override
	protected void afterInvoke() throws Exception {
		
	}

	
	
	public List<Map<String,Object>>  queryAllManagerUser(BaseInputMessage inputMessage){
		return managerUserDao.queryAllManagerUser(ManagerUserDao.class, inputMessage);
	}
	
	
	public Map<String,Object>  queryManagerUser(BaseInputMessage inputMessage){
		return managerUserDao.queryManagerUser(ManagerUserDao.class, inputMessage);
	}
	
	public void  updateOmsAccount(BaseInputMessage inputMessage){
		 managerUserDao.updateOmsAccount(ManagerUserDao.class, inputMessage);
	}

	public List<Map<String,Object>> queryAllMenu() {
		return managerUserDao.queryAllMenu(ManagerUserDao.class, inputMessage);
	}

	public List<Map<String,Object>> queryUserRoleMenu(BaseInputMessage inputMessage) {
		return managerUserDao.queryUserRoleMenu(ManagerUserDao.class, inputMessage);
	}

	public List<Map<String,Object>> getUserRoleMenuList(BaseInputMessage inputMessage) {
		return managerUserDao.getUserRoleMenuList(ManagerUserDao.class, inputMessage);
	}

	public int deleteRoleMenu(BaseInputMessage inputMessage) {
		return managerUserDao.deleteRoleMenu(ManagerUserDao.class, inputMessage);
	}

	public int saveRoleMenu(BaseInputMessage inputMessage) throws Exception{
		 return managerUserDao.saveRoleMenu(ManagerUserDao.class, inputMessage);
	}

	public List<Map<String,Object>> getRoleList() {
		return managerUserDao.getRoleList(ManagerUserDao.class, inputMessage);
	}

    public List<Map<String,Object>>  getUserListByRoleId(BaseInputMessage inMessage) {
		return managerUserDao.getUserListByRoleId(ManagerUserDao.class, inMessage);
    }

	public List<Map<String,Object>> getUserModuleByUserId(BaseInputMessage inMessage) {
		return managerUserDao.getUserModuleByUserId(ManagerUserDao.class, inMessage);
	}

	public int deleteUserModule(BaseInputMessage inMessage) {
		return managerUserDao.deleteUserModule(ManagerUserDao.class, inMessage);
	}

	public int saveUserModule(BaseInputMessage inMessage) {
		return managerUserDao.saveUserModule(ManagerUserDao.class, inMessage);
	}

	public int addRole(BaseInputMessage inMessage) {
		return managerUserDao.addRole(ManagerUserDao.class, inMessage);
	}

	public int createUser(BaseInputMessage inMessage) {
		return managerUserDao.createUser(ManagerUserDao.class, inMessage);
	}

	public int resetPassword(BaseInputMessage inMessage) {
			return managerUserDao.resetPassword(ManagerUserDao.class, inMessage);
	}

	public Map<String,Object> queryManagerUserByUserId(BaseInputMessage inMessage) {
		return managerUserDao.queryManagerUserByUserId(ManagerUserDao.class, inMessage);
	}

    public List<Map<String,Object>> getAllUserInfoList(BaseInputMessage inMessage) {
		return managerUserDao.getAllUserInfoList(ManagerUserDao.class, inMessage);
    }

	public Map<String,Object> getAllUserInfoListCount(BaseInputMessage inMessage) {
		return managerUserDao.getAllUserInfoListCount(ManagerUserDao.class, inMessage);
	}
}
