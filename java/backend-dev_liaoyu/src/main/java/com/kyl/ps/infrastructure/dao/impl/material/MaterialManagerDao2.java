package com.kyl.ps.infrastructure.dao.impl.material;

import com.kyl.ps.infrastructure.dao.MDSSupportCommonDAOImpl;
import com.kyl.ps.infrastructure.dao.Namingspace;
import com.kyl.ps.model.manageruser.ManagerUser;
import com.kyl.ps.pojo.BaseInputMessage;
import org.apache.ibatis.annotations.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Map;

/**
 * <p>Title: UserDao.java</p>
 * <p>Description: com.kyl.ps.infrastructure.dao.impl</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2015年1月4日
 *
 */
@Repository(value ="materialManagerDao")
public interface MaterialManagerDao2 {
		/**
		 * @param requestMap 中参数 category_name
		 *  @param requestMap 中参数 create_time
		 * **/
		public int  material_addCategory(Map  requestMap);
		/**
		 * @param requestMap 中参数category_name是否存在 不存在 0 存在 1
		 * *
		 * */
	    public int material_queryCategoryName(Map requestMap);

}
