package com.kyl.ps.infrastructure.dao.impl.sticker;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Repository;

import com.kyl.ps.infrastructure.dao.MDSSupportCommonDAOImpl;
import com.kyl.ps.infrastructure.dao.Namingspace;
import com.kyl.ps.model.manageruser.ManagerUser;
import com.kyl.ps.pojo.BaseInputMessage;

/**
 * 贴纸管理dao
 * 
 * @author xiao.liao
 *
 */
@Repository
@Namingspace("sticker")
public class StickerDao extends MDSSupportCommonDAOImpl {
	public void insertTemplate(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		sqlSessionTemplate.insert(warpSqlstatement(clazz, "insertTemplate"),
				inputMessage.getRequestMap());
	}
	
	public List<Map<String, Object>> selectTemplates(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "selectTemplates"),
				inputMessage.getRequestMap());
	}
	
	
	public void insertCreations(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		sqlSessionTemplate.insert(warpSqlstatement(clazz, "insertCreations"),
				inputMessage.getRequestMap());
	}
	public void updateCreation(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		sqlSessionTemplate.update(warpSqlstatement(clazz, "updateCreation"),
				inputMessage.getRequestMap());
	}
	public void updateCreationByName(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		sqlSessionTemplate.update(warpSqlstatement(clazz, "updateCreationByName"),
				inputMessage.getRequestMap());
	}
	public void insertStickers(Class<? extends Object> clazz,
			Map<String, Object> map) {
		sqlSessionTemplate.insert(warpSqlstatement(clazz, "insertStickers"),
				map);
	}
	public void insertCreationsRetKey(Class<? extends Object> clazz,
			ManagerUser managerUser) {
		sqlSessionTemplate.insert(warpSqlstatement(clazz, "insertCreationsRetKey"),
				managerUser);
	}
	
	public List<Map<String, Object>> selectCreations(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "selectCreations"),
				inputMessage.getRequestMap());
	}
	public List<Map<String, Object>> selectAllCreations(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "selectAllCreations"),
				inputMessage.getRequestMap());
	}
	
	public List<Map<String, Object>> selectStickers(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "selectStickers"),
				inputMessage.getRequestMap());
	}
	public List<Map<String, Object>> selectStickersBycreationName(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectList(warpSqlstatement(clazz, "selectStickersBycreationName"),
				inputMessage.getRequestMap());
	}
	public int selectStickersCount(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "selectStickersCount"),
				inputMessage.getRequestMap());
	}
	public int selectCreationsCount(Class<? extends Object> clazz,
			BaseInputMessage inputMessage) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "selectCreationsCount"),
				inputMessage.getRequestMap());
	}
	
	
	
	public int selectStickerCountByAreaCode(Class<? extends Object> clazz,
			Map<String, Object> map) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "selectStickerCountByAreaCode"),
				map);
	}
	public int selectAreaPrefixCode(Class<? extends Object> clazz,
			Map<String, Object> map) {
		return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "selectAreaPrefixCode"),
				map);
	}
}
