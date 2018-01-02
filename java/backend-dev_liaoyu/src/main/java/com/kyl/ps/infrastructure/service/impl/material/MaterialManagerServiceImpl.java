package com.kyl.ps.infrastructure.service.impl.material;

import com.kyl.ps.infrastructure.dao.impl.account.ManagerUserDao;
import com.kyl.ps.infrastructure.dao.impl.material.MaterialManagerDao;
import com.kyl.ps.infrastructure.dao.impl.material.MaterialManagerDao2;
import com.kyl.ps.pojo.BaseInputMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

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
public class MaterialManagerServiceImpl {

	@Autowired
	MaterialManagerDao materialManagerDao;


	public int addCategory(BaseInputMessage inputMessage){
		return materialManagerDao.addCategory(MaterialManagerDao.class,inputMessage);
	}

	public Map<String,Object> queryCategoryName(BaseInputMessage inputMessage) {
		return materialManagerDao.queryCategoryName(MaterialManagerDao.class,inputMessage);
	}

	public List<Map<String,Object>> getCategoryList(BaseInputMessage inMessage) {
		return materialManagerDao.getCategoryList(MaterialManagerDao.class, inMessage);
	}

	public int deleteCategory(BaseInputMessage inMessage) {
		return materialManagerDao.deleteCategory(MaterialManagerDao.class, inMessage);
	}

	public int modifyCategory(BaseInputMessage inMessage) {
		return materialManagerDao.modifyCategory(MaterialManagerDao.class, inMessage);
	}

	public int saveMaterialInfo(BaseInputMessage inMessage) {
		return materialManagerDao.saveMaterialInfo(MaterialManagerDao.class, inMessage);
	}

	public List<Map<String,Object>> getMaterialListByCategoryId(BaseInputMessage inMessage) {
		return materialManagerDao.getMaterialListByCategoryId(MaterialManagerDao.class, inMessage);
	}

	public int moveCategory(BaseInputMessage inMessage) {
		return materialManagerDao.moveCategory(MaterialManagerDao.class, inMessage);
	}

	public int deleteMaterial(BaseInputMessage inMessage) {
		return materialManagerDao.deleteMaterial(MaterialManagerDao.class, inMessage);
	}

	public Map<String,Object> getMaterialCountByCategoryId(BaseInputMessage inMessage) {
		return materialManagerDao.getMaterialCountByCategoryId(MaterialManagerDao.class, inMessage);
	}

	public int modifyMaterial(BaseInputMessage inMessage) {
		return materialManagerDao.modifyMaterial(MaterialManagerDao.class, inMessage);
	}

    public int moveCategoryBatch(BaseInputMessage inMessage) {
		return materialManagerDao.material_moveCategory_batch(MaterialManagerDao.class, inMessage);
    }
}
