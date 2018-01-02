package com.kyl.ps.util.tag;

import java.util.Iterator;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.jsp.JspException;
import javax.servlet.jsp.tagext.TagSupport;

import org.apache.log4j.Logger;

import com.kyl.ps.infrastructure.dao.mybatis.Page;
import com.kyl.ps.util.Constants;

/**
 * @File: TestController.java
 * @Package: cn.travelsky.ts.interfaces.controller
 * @Description: 分页标签
 * @Author: xiaoliao
 * @Date: 2013-2-1
 */
@SuppressWarnings("serial")
public class PageTag extends TagSupport {
	private static final Logger logger=Logger.getLogger(PageTag.class);
	
	/** Page对象默认KEY的名称 */
	private static final String PAGE_KEY_NAME="page";
	
	/** 查询参数默认的KEY的名称 */
	private static final String REQUEST_PARAMS="requestParams";
	
	/** 默认分页大小 */
	private static final int DEFAULT_PAGE_SIZE = Constants.DEFAULT_PAGE_SIZE;
	
	/** 每页的大小,可以为空 */
	private int pageSize=DEFAULT_PAGE_SIZE;
	
	/** 查询的url,可以为空 */
	private String url;
	
	/**
	 * 输出分页
	 */
	@SuppressWarnings({ "unchecked", "rawtypes" })
	public int doStartTag() throws JspException {
		try {

			HttpServletRequest request= (HttpServletRequest) pageContext.getRequest();
			Page page=(Page) request.getAttribute(PAGE_KEY_NAME);
			if(page==null){
				return SKIP_BODY;
			}

			if(url==null||"".equals(url)){
				url=request.getRequestURI();
			}

			/* 构建form */
			StringBuilder formBuilder=new StringBuilder();
			formBuilder.append("<form id='tvPagerForm' method='post' action='").append(url).append("' style='display:none;'>");
			Map requestParams=(Map) request.getAttribute(REQUEST_PARAMS);
			
			Iterator<String> it=requestParams.keySet().iterator();
			while(it.hasNext()){
				String attrKey=it.next();
				Object attrValue=requestParams.get(attrKey);
				formBuilder.append("<input type='hidden' id='").append(attrKey).append("' name='").append(attrKey).append("' value='").append(attrValue).append("'/>");
			}
			
			formBuilder.append("</form>");
			
			/* 构建Javascript */
			StringBuilder jsBuilder=new StringBuilder("<script type=\"text/javascript\">function gotoPage(curPageNo){");
			jsBuilder.append("if(curPageNo > 0){$(\"#start\").val(curPageNo);$(\"#tvPagerForm\").submit();}");
			jsBuilder.append("}</script>");
			
			jsBuilder.append("<script type=\"text/javascript\">function goto(totalPageNo){");
			jsBuilder.append("if(isNaN($(\"#pnum\").val())){return false;}");
			jsBuilder.append("if($(\"#pnum\").val() < 1){$(\"#start\").val(1);}");
			jsBuilder.append("else if($(\"#pnum\").val() > totalPageNo){$(\"#start\").val(totalPageNo);}");
			jsBuilder.append("else{$(\"#start\").val($(\"#pnum\").val());}");
			jsBuilder.append("$(\"#tvPagerForm\").submit();");
			jsBuilder.append("}</script>");
			
			/* 构建分页信息 */
			StringBuilder pageTextFormat = new StringBuilder();
			pageTextFormat.append("<div class=\"page\"><ul>");
			
			pageTextFormat.append("<li><a href=\"javascript:gotoPage(1)\" class=\"pg_index\">首页</a></li>");
			
			if (page.getCurrentPageNo() - 1 == 0) {
				pageTextFormat.append("<li><a href=\"javascript:gotoPage(1)\" class=\"pg_next\">上一页</a></li>");
			} else {
				pageTextFormat.append("<li><a href=\"javascript:gotoPage("+(page.getCurrentPageNo() - 1)+")\" class=\"pg_next\">上一页</a></li>");
			}
			
			int begin = page.getCurrentPageNo() - 4 < 1 ? 1:page.getCurrentPageNo() - 4;
			int end = page.getCurrentPageNo() - 1;
			for (int i = begin; i <= end; i++) {
				if (i <= page.getLastPageNo()) {
					pageTextFormat.append("<li><a href=\"javascript:gotoPage("+i+")\">"+i+"</a></li>");
				}
			}
			pageTextFormat.append("<li><a href=\"javascript:gotoPage("+page.getCurrentPageNo()+")\" class=\"pg_selected\">"+page.getCurrentPageNo()+"</a></li>");
			begin = page.getCurrentPageNo() + 1;
			end = page.getCurrentPageNo() + 4;
			for (int i = begin; i <= end; i++) {
				if (i <= page.getLastPageNo()) {
					pageTextFormat.append("<li><a href=\"javascript:gotoPage("+i+")\">"+i+"</a></li>");
				}
			}
			
			if (page.getCurrentPageNo() + 1 < page.getLastPageNo()) {
				pageTextFormat.append("<li><a href=\"javascript:gotoPage("+(page.getCurrentPageNo()+1)+")\" class=\"pg_next\">下一页</a></li>");
			} else if (page.getCurrentPageNo() + 1 >= page.getLastPageNo()){
				pageTextFormat.append("<li><a href=\"javascript:gotoPage("+page.getLastPageNo()+")\" class=\"pg_next\">下一页</a></li>");
			}
			pageTextFormat.append("<li><a href=\"javascript:gotoPage("+page.getLastPageNo()+")\" class=\"pg_last\">尾页</a></li>");
			
			pageTextFormat.append("<li>跳转到第<input onpaste=\"return false;\" oncopy=\"return false;\" oncut=\"return false;\" onkeydown=\"if(event.keyCode==13)event.keyCode=9\" onKeypress=\"if ((event.keyCode<48 || event.keyCode>57)) event.returnValue=false\" id=\"pnum\" name=\"pnum\" value=\""+page.getCurrentPageNo()+"\" style=\"width:40px;\" />页  </li>");
			pageTextFormat.append("<li><a href=\"javascript:goto("+page.getLastPageNo()+")\">确定</a></li>");
			
			pageTextFormat.append("</ul>");
			pageTextFormat.append("<p>共有 "+page.getTotal()+" 条数据，当前第 "+page.getCurrentPageNo()+" / "+page.getLastPageNo()+" 页</p>");
			pageTextFormat.append("</div>");
			
			/* 最后可以把REQUEST_PARAMS清除了 */
			//request.removeAttribute(REQUEST_PARAMS);
			
			/* 输出 */
			pageContext.getOut().write(pageTextFormat.toString() + formBuilder.toString() + jsBuilder.toString());
		} catch (Exception ee) {
			logger.error("输出分页出错", ee);			
		}
		return SKIP_BODY;
	}

	public int doEndTag() throws JspException {
		return EVAL_PAGE;//正常执行接下来的页面
	}

	public int getPageSize() {
		return pageSize;
	}

	public void setPageSize(int pageSize) {
		this.pageSize = pageSize;
	}

	public String getUrl() {
		return url;
	}

	public void setUrl(String url) {
		this.url = url;
	}

}
