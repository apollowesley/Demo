package com.kyl.ps.infrastructure.service.impl.recycler;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.kyl.ps.infrastructure.dao.impl.recycler.RecyclerDao;
import com.kyl.ps.infrastructure.service.AbstractService;
import com.kyl.ps.pojo.BaseInputMessage;

@Service
public class RecyclerServiceImpl extends AbstractService{

	@Autowired
	private RecyclerDao recyclerDao;
	
	@Override
	public void invoke() throws Exception {
	}
	public void insertRecycler(BaseInputMessage inMessage) throws Exception {
		recyclerDao.insertRecycler(RecyclerDao.class, inMessage);		
	}
	public void editRecycler(BaseInputMessage inMessage) throws Exception {
		recyclerDao.editRecycler(RecyclerDao.class, inMessage);		
	}
	@Override
	protected void beforeInvoke() throws Exception {
		
	}
	@Override
	protected void afterInvoke() throws Exception {
		
	}
	
	public List<Map<String,Object>> queryRecycles(BaseInputMessage inMessage){
		return recyclerDao.queryRecycles(RecyclerDao.class, inMessage);
	}
	public List<Map<String,Object>> queryAllRecycles(BaseInputMessage inMessage){
		return recyclerDao.queryAllRecycles(RecyclerDao.class, inMessage);
	}
	public int queryRecyclesCount(BaseInputMessage inMessage){
		return recyclerDao.queryRecyclesCount(RecyclerDao.class, inMessage);
	}
}
