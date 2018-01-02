package com.kyl.ps.infrastructure.service.impl.dict;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.kyl.ps.infrastructure.dao.impl.dict.DictDao;
import com.kyl.ps.infrastructure.service.AbstractService;
import com.kyl.ps.pojo.BaseInputMessage;

@Service
public class DictServiceImpl extends AbstractService{

	@Autowired
	private DictDao dictDao;
	
	@Override
	public void invoke() throws Exception {
	}
	@Override
	protected void beforeInvoke() throws Exception {
		
	}
	@Override
	protected void afterInvoke() throws Exception {
		
	}
	
	public List<Map<String,Object>> queryGaedens(BaseInputMessage inMessage){
		return dictDao.queryGaedens(DictDao.class, inMessage);
	}
}
