package com.kyl.ps.infrastructure.dao.impl.feedback;

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
@Namingspace("feedbackManager")
public class FeedbackManagerDao extends MDSSupportCommonDAOImpl{
	private String pcsParameters(String[] query){
		String q = new String();
		for (int i = 0; i < query.length; i++) {
			q+="_"+query[i];
		}

		return q;
	}

	public int replyFeedbackInfo(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.update(warpSqlstatement(clazz, "replyFeedbackInfo"), inMessage.getRequestMap());
	}

	public List<Map<String,Object>> getFeedbackInfoList(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getFeedbackInfoList"), inMessage.getRequestMap());
	}

	public Map<String,Object> getFeedbackInfo(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "getFeedbackInfo"), inMessage.getRequestMap());
	}


	public Map<String,Object> getFeedbackInfoPageCount(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "getFeedbackInfoPageCount"), inMessage.getRequestMap());
	}
}
