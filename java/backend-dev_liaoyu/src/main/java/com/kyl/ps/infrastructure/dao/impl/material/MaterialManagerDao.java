package com.kyl.ps.infrastructure.dao.impl.material;

import java.util.List;
import java.util.Map;

import com.kyl.ps.infrastructure.dao.impl.account.ManagerUserDao;
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
 * @author: zxd
 * @date:   2015年1月4日
 *
 */
@Repository
@Namingspace("material")
public class MaterialManagerDao extends MDSSupportCommonDAOImpl{
	private String pcsParameters(String[] query){
		String q = new String();
		for (int i = 0; i < query.length; i++) {
			q+="_"+query[i];
		}

		return q;
	}
	public Map<String,Object>  queryCategoryName(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "queryCategoryName"), inputMessage.getRequestMap());
	}

	public int addCategory(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.insert(warpSqlstatement(clazz, "addCategory"), inputMessage.getRequestMap());
	}

	public List<Map<String,Object>> getCategoryList(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getCategoryList"), inMessage.getRequestMap());
	}

	public int deleteCategory(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.delete(warpSqlstatement(clazz, "deleteCategory"), inMessage.getRequestMap());
	}

	public int modifyCategory(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.delete(warpSqlstatement(clazz, "modifyCategory"), inMessage.getRequestMap());
	}

	public int saveMaterialInfo(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.insert(warpSqlstatement(clazz, "saveMaterialInfo"), inMessage.getRequestMap());
	}

	public List<Map<String,Object>> getMaterialListByCategoryId(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getMaterialListByCategoryId"), inMessage.getRequestMap());
	}

	public int moveCategory(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.update(warpSqlstatement(clazz, "moveCategory"), inMessage.getRequestMap());
	}

	public int deleteMaterial(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.delete(warpSqlstatement(clazz, "deleteMaterial"), inMessage.getRequestMap());
	}

	public Map<String,Object> getMaterialCountByCategoryId(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "getMaterialCountByCategoryId"), inMessage.getRequestMap());
	}

	public int modifyMaterial(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.update(warpSqlstatement(clazz, "modifyMaterial"), inMessage.getRequestMap());
	}

    public int material_moveCategory_batch(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.update(warpSqlstatement(clazz, "moveCategory_batch"), inMessage.getRequestMap());
    }
}
