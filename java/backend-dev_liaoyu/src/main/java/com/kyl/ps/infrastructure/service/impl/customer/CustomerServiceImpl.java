package com.kyl.ps.infrastructure.service.impl.customer;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.kyl.ps.infrastructure.dao.impl.customer.CustomerDao;
import com.kyl.ps.infrastructure.service.AbstractService;
import com.kyl.ps.pojo.BaseInputMessage;

@Service
public class CustomerServiceImpl extends AbstractService{

	@Autowired
	private CustomerDao customerDao;
	
	@Override
	public void invoke() throws Exception {
	}
	@Override
	protected void beforeInvoke() throws Exception {
		
	}
	@Override
	protected void afterInvoke() throws Exception {
		
	}
	public void insertCustomer(BaseInputMessage inMessage) throws Exception {
		customerDao.insertCustomer(CustomerDao.class, inMessage);	
	}
	public void updateUserMobileById(BaseInputMessage inMessage) throws Exception {
		customerDao.updateUserMobileById(CustomerDao.class, inMessage);	
	}
	
	public Map<String,Object> queryCustomerInfo(BaseInputMessage inMessage){
		return customerDao.queryCustomerInfo(CustomerDao.class, inMessage);
	}
	public Map<String,Object> queryUserMobileById(BaseInputMessage inMessage){
		return customerDao.queryUserMobileById(CustomerDao.class, inMessage);
	}
	
	public int queryUsagerecordCount(BaseInputMessage inMessage){
		return customerDao.queryUsagerecordCount(CustomerDao.class, inMessage);
	}
	
	public List<Map<String, Object>> queryUsagerecord(BaseInputMessage inMessage){
		return customerDao.queryUsagerecord(CustomerDao.class, inMessage);
	}
	public List<Map<String, Object>> queryAllUser(BaseInputMessage inMessage){
		return customerDao.queryAllUser(CustomerDao.class, inMessage);
	}
	public List<Map<String, Object>> queryAllUserExtend(BaseInputMessage inMessage){
		return customerDao.queryAllUserExtend(CustomerDao.class, inMessage);
	}
}
