package com.kyl.ps.util;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import net.sf.json.JSONObject;

import org.apache.commons.lang.StringUtils;

import com.kyl.ps.model.account.Role;

/**
 * 生成随机数方法
 * <p>Title: RandNumGenerator.java</p>
 * <p>Description: com.kyl.ps.util</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2014年12月8日
 *
 */
public class RandNumGenerator
{

	/**
	 * 私有构造
	 */
	private RandNumGenerator() {
	}

	/**
	 * 
	 * @Description：生成六位不带字母的随机数
	 * @author: xiaoliao
	 * @date:   2014年12月8日
	 *
	 * @return
	 */
	@SuppressWarnings("rawtypes")
	public synchronized static String generateRandNum() {  
        String[] beforeShuffle = new String[] { "1", "2", "3", "4", "5", "6", "7", "8", "9" };  
        List list = Arrays.asList(beforeShuffle);  
        Collections.shuffle(list);  
        StringBuilder sb = new StringBuilder();  
        for (int i = 0; i < list.size(); i++) {  
            sb.append(list.get(i));  
        }  
        String afterShuffle = sb.toString();  
        String result = afterShuffle.substring(0, 6);
        result = StringUtils.rightPad(result, 6, "0");
        return result;  
    }
	
	/**
	 * 
	 * @Description：生成六位带字母的随机数
	 * @author: xiaoliao
	 * @date:   2014年12月8日
	 *
	 * @return
	 */
	@SuppressWarnings("rawtypes")
	public synchronized static String generateRandNumIncludeWord() {  
        String[] beforeShuffle = new String[] { "1", "2", "3", "4", "5", "6", "7", "8", "9", 
        		"A", "B", "C", "D", "E", "F", "G", "H", "I", "J",  
                "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",  
                "W", "X", "Y", "Z"};  
        List list = Arrays.asList(beforeShuffle);  
        Collections.shuffle(list);  
        StringBuilder sb = new StringBuilder();  
        for (int i = 0; i < list.size(); i++) {  
            sb.append(list.get(i));  
        }  
        String afterShuffle = sb.toString();  
        String result = afterShuffle.substring(0, 6);
        result = StringUtils.rightPad(result, 6, "0");
        return result;  
    }
	
	public static void main(String[] args) {
		System.out.println(generateRandNum());
		Role role = new Role();
		role.setId("123");
		role.setRoleName("test");
		role.setShowFlag("flag");
		System.out.println(JSONObject.fromObject(role).toString());
	}
}
