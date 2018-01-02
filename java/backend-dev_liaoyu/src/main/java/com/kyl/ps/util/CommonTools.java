package com.kyl.ps.util;

import java.util.List;
import java.util.Random;



/**
 * 常用操作方法
 * 
 * @author Andy
 *
 */
public class CommonTools {

	public static String setDefault(String value, String def) {
		if (value == null || value.trim().length() <= 0) {
			if (def != null && def.trim().length() > 0) {
				return String.valueOf(def);
			} else {
				return "";
			}
		}
		return String.valueOf(value);
	}

	public static String setDefault(Object value, String def) {
		if (value == null || ((String) value).trim().length() <= 0) {
			if (def != null && def.trim().length() > 0) {
				return String.valueOf(def);
			} else {
				return "";
			}
		}
		return String.valueOf(value);
	}

	public static Integer setDefault(String value, Integer def) {
		if (value == null) {
			if (def != null) {
				return def;
			} else {
				return 0;
			}
		}
		return Integer.valueOf(value);
	}
	
	public static Integer setDefault(Integer value, Integer def) {
		if (value == null) {
			if (def != null) {
				return def;
			} else {
				return 0;
			}
		}
		return value;
	}

	public static Long setDefault(String value, Long def) {
		if (value == null) {
			if (def != null) {
				return def;
			} else {
				return 0l;
			}
		}
		return Long.valueOf(value);
	}

	public static boolean check(String str) {
		if (str != null && str.trim().length() > 0) {
			return true;
		}
		return false;
	}

	public static boolean isEmpty(String str) {
		if (str != null && str.trim().length() > 0) {
			return false;
		}
		return true;
	}

	public static boolean isNotEmpty(String str) {
		if (str != null && str.trim().length() > 0) {
			return true;
		}
		return false;
	}

	public static <E> boolean check(List<E> list) {
		if (list != null && list.size() > 0) {
			return true;
		}
		return false;
	}

	public static Integer random(int min, int max) {
		Random random = new Random();
		int result = random.nextInt(max) % (max - min + 1) + min;
		return result;
	}

	public static String covertNull(String str) {
		if (str != null && str.trim().length() > 0) {
			return str;
		}
		return "";
	}

	public static boolean isBraceEmpty(String str) {
		if (replaceBrace(str).equals(""))
			return true;
		return false;
	}

	public static String replaceBrace(String str) {
		if (str != null && str.trim().length() > 0) {
			str = str.replace("{", "");
			str = str.replace("}", "");
			return str.trim();
		}
		return "";
	}

	public static Object classInstance(String clzz) throws Exception {
		Object instance = Class.forName(clzz).newInstance();
		return instance;
	}
	
	public static String escapeJson(String str) {
		if (str != null && str.trim().length() > 0) {
			str = str.replaceAll(":", "：").replaceAll("\"", "“");
			str = str.replaceAll("\\", "/");
			return str.trim();
		}
		return "";
	}
}
