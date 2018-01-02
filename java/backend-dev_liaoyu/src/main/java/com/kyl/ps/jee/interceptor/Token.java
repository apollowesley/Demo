package com.kyl.ps.jee.interceptor;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * <p>Title: Token.java</p>
 * <p>Description: com.kyl.ps.jee.interceptor</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2014年12月17日
 *
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Token {
	boolean save() default false;
	 
    boolean remove() default false;
}
