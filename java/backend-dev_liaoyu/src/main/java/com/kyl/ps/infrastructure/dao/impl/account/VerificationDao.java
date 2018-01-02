package com.kyl.ps.infrastructure.dao.impl.account;

import org.springframework.stereotype.Repository;

import com.kyl.ps.infrastructure.dao.MDSSupportCommonDAOImpl;
import com.kyl.ps.infrastructure.dao.Namingspace;
import com.kyl.ps.pojo.BaseInputMessage;

@Repository
@Namingspace("verification")
public class VerificationDao extends MDSSupportCommonDAOImpl{
	 public void insertCode(Class<? extends Object> clazz,BaseInputMessage inputMessage) {
	        sqlSessionTemplate.insert(warpSqlstatement(clazz, "insertCode"),inputMessage.getRequestMap());
	    }
	 public int CodeShuMu(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
			return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "CodeShuMu"), inputMessage.getRequestMap());
		} 
	 public int selectCode(Class<? extends Object> clazz, BaseInputMessage inputMessage) {
			return sqlSessionTemplate.selectOne(warpSqlstatement(clazz, "selectCode"), inputMessage.getRequestMap());
		} 
}
