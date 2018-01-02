package com.kyl.ps.infrastructure.dao.impl.area;

import com.kyl.ps.infrastructure.dao.MDSSupportCommonDAOImpl;
import com.kyl.ps.infrastructure.dao.Namingspace;
import com.kyl.ps.pojo.BaseInputMessage;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Map;

/**
 * <p>Title: UserDao.java</p>
 * <p>Description: com.kyl.ps.infrastructure.dao.impl</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: zxd
 * @date:   2015年1月4日
 *
 */
@Repository
@Namingspace("areaManager")
public class AreaManagerDao extends MDSSupportCommonDAOImpl{
	private String pcsParameters(String[] query){
		String q = new String();
		for (int i = 0; i < query.length; i++) {
			q+="_"+query[i];
		}

		return q;
	}

	public List<Map<String,Object>> getUserAreaList(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getUserAreaList"), inMessage.getRequestMap());
	}

	public Map<String,Object> getUserAreaPlot(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "getUserAreaPlot"), inMessage.getRequestMap());
	}

	public int addUserAreaPlot(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.insert(warpSqlstatement(clazz, "addUserAreaPlot"), inMessage.getRequestMap());
	}

	public int modifyUserAreaPlot(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.update(warpSqlstatement(clazz, "modifyUserAreaPlot"), inMessage.getRequestMap());
	}

	public List<Map<String,Object>> getAreaList(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getAreaList"), inMessage.getRequestMap());
	}

	public List<Map<String,Object>> getPlotListByAreaId(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getPlotListByAreaId"), inMessage.getRequestMap());
	}

	public List<Map<String,Object>> getSystemPushMessageList(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getSystemPushMessageList"), inMessage.getRequestMap());
	}

	public Map<String,Object> getSystemPushMessageListCount(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "getSystemPushMessageListCount"), inMessage.getRequestMap());
	}
	public int  createSystemPushMessage(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.insert(warpSqlstatement(clazz, "createSystemPushMessage"), inMessage.getRequestMap());

	}

    public List<Map<String,Object>> getCityUserAreaList(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getCityUserAreaList"), inMessage.getRequestMap());
    }
	public List<Map<String,Object>> getDistUserAreaList(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getDistUserAreaList"), inMessage.getRequestMap());
	}

    public int deletePlot(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.delete(warpSqlstatement(clazz, "deletePlot"), inMessage.getRequestMap());
    }

	public List<Map<String,Object>> queryAllSystemMessage(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "queryAllSystemMessage"), inMessage.getRequestMap());
	}
}
