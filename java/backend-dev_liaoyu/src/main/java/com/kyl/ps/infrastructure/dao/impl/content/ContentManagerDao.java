package com.kyl.ps.infrastructure.dao.impl.content;

import com.kyl.ps.infrastructure.dao.MDSSupportCommonDAOImpl;
import com.kyl.ps.infrastructure.dao.Namingspace;
import com.kyl.ps.infrastructure.dao.impl.material.MaterialManagerDao;
import com.kyl.ps.pojo.BaseInputMessage;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Map;
@Repository
@Namingspace("content")
public class ContentManagerDao extends MDSSupportCommonDAOImpl {
	private String pcsParameters(String[] query) {
		String q = new String();
		for (int i = 0; i < query.length; i++) {
			q += "_" + query[i];
		}

		return q;
	}
	public Map<String,Object>  queryCategoryName(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "queryCategoryName"), inputMessage.getRequestMap());
	}
	public int addColumn(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
		return sqlSessionTemplate.insert(warpSqlstatement(clazz, "addColumn"), inputMessage.getRequestMap());
	}

	public int modifyColumn(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.update(warpSqlstatement(clazz, "modifyColumn"), inMessage.getRequestMap());
	}
	public int modifyColumnOrder(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.update(warpSqlstatement(clazz, "modifyColumnOrder"), inMessage.getRequestMap());
	}
    public List<Map<String,Object>> getColumnList(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getColumnList"), inMessage.getRequestMap());
    }

	public int addContentInfo(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.insert(warpSqlstatement(clazz, "addContentInfo"), inMessage.getRequestMap());
	}

	public int modifyContentInfo(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.update(warpSqlstatement(clazz, "modifyContentInfo"), inMessage.getRequestMap());
	}

	public Map<String,Object> getColumnContentCountByColumnId(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "getColumnContentCountByColumnId"), inMessage.getRequestMap());
	}

	public List<Map<String,Object>> getColumnContentByColumnId(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "getColumnContentByColumnId"), inMessage.getRequestMap());
	}

	public Map<String,Object> getColumnArticleByArticleId(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "getColumnArticleByArticleId"), inMessage.getRequestMap());
	}

	public int deleteArticle(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.delete(warpSqlstatement(clazz, "deleteArticle"), inMessage.getRequestMap());
	}

	public int stickArticle(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.delete(warpSqlstatement(clazz, "stickArticle"), inMessage.getRequestMap());
	}

	public int deleteColumn(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.delete(warpSqlstatement(clazz, "deleteColumn"), inMessage.getRequestMap());
	}

    public int moveColumn(Class<? extends Object> clazz, BaseInputMessage inMessage) {
		return sqlSessionTemplate.delete(warpSqlstatement(clazz, "moveColumn"), inMessage.getRequestMap());
    }
}
