package com.kyl.ps.infrastructure.service.impl.collect;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.kyl.ps.infrastructure.dao.impl.collect.CollectDao;
import com.kyl.ps.infrastructure.service.AbstractService;
import com.kyl.ps.pojo.BaseInputMessage;

@Service
public class CollectServiceImpl extends AbstractService{

	@Autowired
	private CollectDao collectDao;
	
	@Override
	protected void beforeInvoke() throws Exception {
		
	}
	@Override
	protected void afterInvoke() throws Exception {
		
	}
	@Override
	public void invoke() throws Exception {
	}
	
	
	public List<Map<String, Object>> queryKitchenBySid(BaseInputMessage inMessage)throws Exception {
		return collectDao.queryKitchenBySid(CollectDao.class, inMessage);
	}
	public List<Map<String, Object>> queryGarbageBySid(BaseInputMessage inMessage)throws Exception {
		return collectDao.queryGarbageBySid(CollectDao.class, inMessage);
	}
	public int queryKitchenBySidCount(BaseInputMessage inMessage)throws Exception {
		return collectDao.queryKitchenBySidCount(CollectDao.class, inMessage);
	}
	public int queryGarbageBySidCount(BaseInputMessage inMessage)throws Exception {
		return collectDao.queryGarbageBySidCount(CollectDao.class, inMessage);
	}
	
}
