package com.kyl.ps.infrastructure.dao;

import java.util.logging.Logger;

import org.springframework.jdbc.datasource.lookup.AbstractRoutingDataSource;

/**
 * <p>Title: DataSources.java</p>
 * <p>Description: com.kyl.ps.infrastructure.dao</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2014年11月13日
 *
 */
public class DataSources extends AbstractRoutingDataSource{

	public Logger getParentLogger(){
		return null;
	}

	@Override
	protected Object determineCurrentLookupKey() {
		return DataSourceSwitch.getDataSourceType();  
	}

}
