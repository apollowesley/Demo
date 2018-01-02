package com.kyl.ps.util;

import java.util.Locale;

import org.springframework.beans.BeansException;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;

/**
 * @File: BeanHolder.java
 * @Description: (Description)
 * @Author: xiaoliao
 * @Date: 2012-9-7
 */
public class BeanHolder implements ApplicationContextAware{
	private static ApplicationContext context = null;

	public BeanHolder()
	{

	}

	public void setApplicationContext(ApplicationContext arg0)
			throws BeansException
	{
		setApplicationContextStatic(arg0);
	}

	/**
	 * Private set method, to avoid errors findBug。
	 * 
	 * @param arg0
	 */
	private static void setApplicationContextStatic(ApplicationContext arg0)
	{
		context = arg0;
	}

	/**
	 * get bean obiect according bean name
	 * 
	 * @param String
	 *            bean name
	 */
	public static Object getBean(String name)
	{
		return context.getBean(name);
	}

	/*
	 * The following methods to obtain the resource file
	 */
	public static String getMessage(String msg, Object[] args, Locale locale)
	{
		return context.getMessage(msg, args, msg, locale);
	}

	public static String getMessage(String msg, Object[] args)
	{
		return context.getMessage(msg, args, msg, Locale.getDefault());
	}

	public static String getMessage(String msg)
	{
		return context.getMessage(msg, null, msg, Locale.getDefault());
	}

	public static String getMessage(String msg, Locale locale)
	{
		return context.getMessage(msg, null, msg, locale);
	}
}
