package com.kyl.ps.exception;

import java.util.HashMap;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.web.servlet.HandlerExceptionResolver;
import org.springframework.web.servlet.ModelAndView;

import com.kyl.ps.jee.JEEConstant;
import com.kyl.ps.util.BeanHolder;


/**
 * @File: MyHandlerExceptionResolver.java
 * @Description: 统一异常处理类
 * @Author: xiaoliao
 * @Date: 2012-9-7
 */
public class MyHandlerExceptionResolver implements HandlerExceptionResolver, JEEConstant{

	/**
	 * 统一异常处理类
	 */
	@SuppressWarnings({ "rawtypes", "unchecked" })
	public ModelAndView resolveException(HttpServletRequest arg0,
			HttpServletResponse arg1, Object arg2, Exception ex) {
	
		Map model = new HashMap();
		
		//判断是否是重复提交异常
		if (ex instanceof RepeatCommitException) {
			arg0.getSession(false).removeAttribute(SUBMIT_TOKEN_HISTORY);
			
			model.put("ex", BeanHolder.getMessage(ex.getMessage()));
			return new ModelAndView("errordisplay", model);
		}else {
			if (null != arg0.getSession(false).getAttribute(SUBMIT_TOKEN_HISTORY)) {
				arg0.getSession(false).setAttribute(SUBMIT_TOKEN, arg0.getSession(false).getAttribute(SUBMIT_TOKEN_HISTORY).toString());
			}
		}
		
		try {
			if (!ex.getMessage().equalsIgnoreCase(BeanHolder.getMessage(ex.getMessage()))) {
				model.put("ex", BeanHolder.getMessage(ex.getMessage()));
				return new ModelAndView("errordisplay", model);
			}
		} catch (Exception e) {
			model.put("ex", ex.getMessage());
		}
		
		model.put("ex", ex.getMessage());
		return new ModelAndView("error", model);
	}

}
