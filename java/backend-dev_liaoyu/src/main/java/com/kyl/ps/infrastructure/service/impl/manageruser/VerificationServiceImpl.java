package com.kyl.ps.infrastructure.service.impl.manageruser;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.kyl.ps.infrastructure.dao.impl.account.VerificationDao;
import com.kyl.ps.infrastructure.service.AbstractService;
import com.kyl.ps.pojo.BaseInputMessage;

@Service
public class VerificationServiceImpl extends AbstractService{

	@Autowired
	private VerificationDao verificationDao;
	
	@Override
	public void invoke() throws Exception {
	}
	public void insertCode(BaseInputMessage inMessage) throws Exception {
		verificationDao.insertCode(VerificationDao.class, inMessage);		
	}
	public int CodeShuMu(BaseInputMessage inMessage)throws Exception {
		return verificationDao.CodeShuMu(VerificationDao.class, inMessage);
	}
	public int selectCode(BaseInputMessage inMessage)throws Exception {
		return verificationDao.selectCode(VerificationDao.class, inMessage);
	}
	@Override
	protected void beforeInvoke() throws Exception {
		
	}
	@Override
	protected void afterInvoke() throws Exception {
		
	}
}
