package com.kyl.ps.pojo;

import java.util.Comparator;
import java.util.Map;

public class MyComparator implements Comparator<Object> {

	@SuppressWarnings("rawtypes")
	@Override
	public int compare(Object o1, Object o2) {
		Map map1 = (Map) o1;
		Map map2 = (Map) o2;
		return map2.get("collect_time").toString().compareTo(map1.get("collect_time").toString());
	}

}
