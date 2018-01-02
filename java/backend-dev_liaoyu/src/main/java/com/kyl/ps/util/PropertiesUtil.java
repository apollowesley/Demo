package com.kyl.ps.util;

import java.io.InputStream;
import java.util.Properties;

public class PropertiesUtil {
	
	public static String getValue(String propName,String key){
		InputStream inputStream = PropertiesUtil.class.getClassLoader().getResourceAsStream("properties"+"/"+propName+".properties");   
	    Properties p = new Properties();   
	    try {   
	      p.load(inputStream);   
	    } catch (Exception e1) {   
	      e1.printStackTrace();   
	    } 
	    return p.getProperty(key);
	}
	public static Properties getProperties(String propName) {
		InputStream inputStream = PropertiesUtil.class.getClassLoader().getResourceAsStream(propName + ".properties");
		Properties p = new Properties();
		try {
			p.load(inputStream);
		} catch (Exception e1) {
			e1.printStackTrace();
		}
		return p;
	}
	

	
	public static String getValueForSrc(String propName,String key){
		InputStream inputStream = PropertiesUtil.class.getClassLoader().getResourceAsStream(propName+".properties");   
	    Properties p = new Properties();   
	    try {   
	      p.load(inputStream);   
	    } catch (Exception e1) {   
	      e1.printStackTrace();   
	    } 
	    return p.getProperty(key);
	}
	

	public static Integer getIntValue(Properties property, String key) {
		return Integer.valueOf(property.getProperty(key));
	}

	public static String getStringValue(Properties property, String key) {
		return property.getProperty(key);
	}

	public static Boolean getBooleanValue(Properties property, String key) {
		return Boolean.valueOf(property.getProperty(key));
	}

}
