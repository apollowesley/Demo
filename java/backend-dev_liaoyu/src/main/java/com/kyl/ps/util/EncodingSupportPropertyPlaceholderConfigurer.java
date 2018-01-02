package com.kyl.ps.util;

import java.util.Properties;
import java.util.regex.Pattern;

import org.springframework.beans.factory.config.PropertyPlaceholderConfigurer;

/**
 * <p>Title: EncodingSupportPropertyPlaceholderConfigurer.java</p>
 * <p>Description: com.kyl.ps.util</p>
 * <p>Copyright: Copyright (c) 2015</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2015年1月13日
 *
 */
public class EncodingSupportPropertyPlaceholderConfigurer extends PropertyPlaceholderConfigurer{

	/**
	 * 加密属性正则表达式
	 */
	private String[] encryptionProperties = new String[0]; 
	
	/*
	 * (non-Javadoc)
	 * @see org.springframework.beans.factory.config.PropertyPlaceholderConfigurer#resolvePlaceholder(java.lang.String, java.util.Properties)
	 */
	protected String resolvePlaceholder(String placeholder, Properties props) {

		if (null != encryptionProperties && encryptionProperties.length > 0)
		{
			for (String propertyName : encryptionProperties)
			{
				if (Pattern.matches(propertyName, placeholder))
				{
					DESHelper des=DESHelper.getInstance();
					return des.decrypt(props.getProperty(placeholder));
				}
			}
			return props.getProperty(placeholder);
		}
		else
		{
			return props.getProperty(placeholder);
		}
	}
	
	/**
	 * 设置加密属性过滤正则表达式
	 * @param encryptionProperties
	 */
	public void setEncryptionProperties(String[] encryptionProperties)
	{
		if (encryptionProperties != null)
		{
			this.encryptionProperties = encryptionProperties.clone();
		}
		else
		{
			this.encryptionProperties = null;
		}
	}
	
	public static void main(String[] args) {
		DESHelper des = DESHelper.getInstance();
		System.out.println(des.encrypt("jdbc:mysql://192.168.1.241:3306/businessDb?useUnicode=true&characterEncoding=UTF-8&autoReconnect=true&failOverReadOnly=false"));
		System.out.println(des.encrypt("original"));
		System.out.println(des.encrypt("celong1025"));
		
		System.out.println(des.encrypt("root"));
		System.out.println(des.encrypt("kylkj2015"));
		
		
		
		System.out.println("=================");
		System.out.println(des.decrypt("dJOtD0pk3E1SxC2U8MYopYwaYM1LwU9dP70THSB7nUm/mty0LlulCOsWDMsf/4YlAqWFZFOzHtHtJLtueioO/ShQfqQI/MBRt0/76qOw+qOf4p+4cACjjJf+FkI3Y1TqIUDPZ8Hi4kqODvOwawIZBJNauM3O0qPO+wU3u+teKO3Xc2luLnGs2w=="));
		System.out.println(des.decrypt("6ZzItieTHH4="));
		System.out.println(des.decrypt("PS4okTbVAYI=="));
	}
}
