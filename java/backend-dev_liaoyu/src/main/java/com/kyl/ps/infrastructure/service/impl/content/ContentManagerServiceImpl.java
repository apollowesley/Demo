package com.kyl.ps.infrastructure.service.impl.content;

import com.kyl.ps.infrastructure.dao.impl.content.ContentManagerDao;
import com.kyl.ps.infrastructure.dao.impl.material.MaterialManagerDao;
import com.kyl.ps.infrastructure.service.AbstractService;
import com.kyl.ps.pojo.BaseInputMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import javax.swing.text.AbstractDocument;
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
public class ContentManagerServiceImpl extends AbstractService {

	@Autowired
	ContentManagerDao contentManagerDao;

	public int addColumn(BaseInputMessage inMessage) {
		return contentManagerDao.addColumn(ContentManagerDao.class,inMessage);
	}

	public int modifyColumn(BaseInputMessage inMessage) {
		return contentManagerDao.modifyColumn(ContentManagerDao.class,inMessage);
	}

    public List<Map<String,Object>>  getColumnList() {
		return contentManagerDao.getColumnList(ContentManagerDao.class, inputMessage);
    }
	public int modifyColumnOrder(BaseInputMessage inMessage) {
		return contentManagerDao.modifyColumnOrder(ContentManagerDao.class,inMessage);
	}

	public int  addContentInfo(BaseInputMessage inMessage) {
		return contentManagerDao.addContentInfo(ContentManagerDao.class,inMessage);
	}
	@Override
	protected void beforeInvoke() throws Exception {

	}

	@Override
	public void invoke() throws Exception {
	}

	@Override
	protected void afterInvoke() throws Exception {

	}

	public int modifyContentInfo(BaseInputMessage inMessage) {
		return contentManagerDao.modifyContentInfo(ContentManagerDao.class,inMessage);
	}

	public Map<String,Object> getColumnContentCountByColumnId(BaseInputMessage inMessage) {
		return contentManagerDao.getColumnContentCountByColumnId(ContentManagerDao.class,inMessage);
	}

	public List<Map<String,Object>> getColumnContentByColumnId(BaseInputMessage inMessage) {
		return contentManagerDao.getColumnContentByColumnId(ContentManagerDao.class,inMessage);
	}

	public Map<String,Object> getColumnArticleByArticleId(BaseInputMessage inMessage) {
		return  contentManagerDao.getColumnArticleByArticleId(ContentManagerDao.class,inMessage);
	}

	public int deleteArticle(BaseInputMessage inMessage) {
		return  contentManagerDao.deleteArticle(ContentManagerDao.class,inMessage);
	}

	public int stickArticle(BaseInputMessage inMessage) {
		return  contentManagerDao.stickArticle(ContentManagerDao.class,inMessage);
	}

	public int deleteColumn(BaseInputMessage inMessage) {
		return  contentManagerDao.deleteColumn(ContentManagerDao.class,inMessage);
	}

    public int  moveColumn(BaseInputMessage inMessage) {
		return  contentManagerDao.moveColumn(ContentManagerDao.class,inMessage);
    }


    /****
	public int addCategory(BaseInputMessage inputMessage){
		return contentManagerDao.addCategory(MaterialManagerDao.class,inputMessage);
	}

	public Map<String,Object> queryCategoryName(BaseInputMessage inputMessage) {
		return contentManagerDao.queryCategoryName(MaterialManagerDao.class,inputMessage);
	}

	public List<Map<String,Object>> getCategoryList(BaseInputMessage inMessage) {
		return contentManagerDao.getCategoryList(MaterialManagerDao.class, inMessage);
	}
	**/

}
