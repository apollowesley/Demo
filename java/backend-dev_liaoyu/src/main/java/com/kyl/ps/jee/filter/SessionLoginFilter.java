package com.kyl.ps.jee.filter;

import java.io.IOException;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.springframework.beans.factory.annotation.Autowired;

import com.kyl.ps.infrastructure.service.impl.manageruser.ManagerUserServiceImpl;
import com.kyl.ps.jee.JEEConstant;

/**
 * Description: 用户登录验证过滤器 如果未登录系统，则直接跳转到登录页面
 * 
 * @author xiaoliao
 */
public class SessionLoginFilter implements Filter, JEEConstant {

	
	@Autowired
	 ManagerUserServiceImpl managerUserServiceImpl;
	/**
	 * 基本排除路径
	 */
	private static final String[] baseExcludeUrl = {"/sticker/saveTemplate","/", "/index.jsp", "/home/index", "/home/login","/home/randnumberimage", "/home/welcome"};//最后五个为接口调用

	public void doFilter(ServletRequest request, ServletResponse response,
			FilterChain chain) throws IOException, ServletException {
		HttpServletRequest httpServletRequest = (HttpServletRequest) request;
		HttpServletResponse httpServletResponse = (HttpServletResponse) response;

		// 当前访问的路径
		final String curURL = httpServletRequest.getRequestURI();
		final String currentURL = curURL.substring(curURL.indexOf("/", 1), curURL.length());
		
		boolean sessionFlag = false;
		
		HttpSession session = httpServletRequest.getSession(false);
		if(null != session){
			sessionFlag = validateSession(session, SESSION_LOGIN_TOKEN);
		}

		if (excludeURL(currentURL, baseExcludeUrl) || currentURL.endsWith(".js")
	        || currentURL.endsWith(".css") || currentURL.endsWith(".png") || currentURL.endsWith(".jpg")) {
			chain.doFilter(request, response);
		}else {
			if(sessionFlag){
				chain.doFilter(httpServletRequest, httpServletResponse);
			}else{
				//httpServletResponse.sendRedirect(httpServletRequest.getContextPath());
				String indexString = httpServletRequest.getContextPath();
				httpServletResponse.getWriter().write("<script>top.location.href=\""+indexString+"\"</script>");
			}
		}
	}

	/**
	 * 
	 * @Description：验证session
	 * @author: xiaoliao
	 * @date:   2014年12月19日
	 *
	 * @param session
	 * @param token
	 * @return
	 */
	private boolean validateSession(HttpSession session, String token) {
		if(null != session.getAttribute(token)){
			return true;
		}else{
			return false;
		}
	}
	
	/**
	 * 
	 * @Description：排除的URL
	 * @author: xiaoliao
	 * @date:   2014年12月19日
	 *
	 * @param url
	 * @param excludeUrl
	 * @return
	 */
	private boolean excludeURL(String url, String[] excludeUrl) {
		for (String exclude : excludeUrl) {
			if (url.equalsIgnoreCase(exclude)) {
				return true;
			}
		}
		return false;
	}

	public void destroy() {
		// TODO Auto-generated method stub
		
	}

	public void init(FilterConfig arg0) throws ServletException {
		// TODO Auto-generated method stub
		
	}

}
