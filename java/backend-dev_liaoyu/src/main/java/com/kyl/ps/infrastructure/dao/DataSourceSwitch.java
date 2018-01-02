package com.kyl.ps.infrastructure.dao;

/**
 * <p>Title: DataSourceSwitch.java</p>
 * <p>Description: com.kyl.ps.infrastructure.dao</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2014年11月13日
 *
 */
public class DataSourceSwitch {
	@SuppressWarnings("rawtypes")
	private static final ThreadLocal contextHolder=new ThreadLocal();  
    
    @SuppressWarnings("unchecked")
	public static void setDataSourceType(String dataSourceType){  
        contextHolder.set(dataSourceType);  
    }  
      
    public static String getDataSourceType(){  
        return (String) contextHolder.get();  
    }  
      
    public static void clearDataSourceType(){  
        contextHolder.remove();  
    }  
}
