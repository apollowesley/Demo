package com.kyl.ps.util;


import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class HtmlRegexpUtil {
	private final static String regxpForHtml = "<([^>]*)>"; // 过滤所有以<开头以>结尾的标签  
    
    public static String filterImgUrl(String str){
    	 Pattern p = Pattern.compile("<img[^>]+src\\s*=\\s*['\"]([^'\"]+)['\"][^>]*>");
         Matcher m = p.matcher(str);
         while(m.find()){
             str=str.replace(m.group(), "&@"+m.group(1)+"&@");
         }
         return str;
    }
    
//    public static String filterImg(String str){
//   	 Pattern p = Pattern.compile("<img[^>]+src\\s*=\\s*['\"]([^'\"]+)['\"][^>]*>");
//        Matcher m = p.matcher(str);
//        String str1="";
//        while(m.find()){
//        	str1+=m.group();
//        }
//        return str1;
//   }
   
    
    public static void main(String[] args) {

	}
}
