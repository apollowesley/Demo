package com.kyl.ps.infrastructure.dao;

/**
 * 
 * 命名空间源注释
 * 类注解，支持继承
 * @author xiaoliao
 */
@java.lang.annotation.Retention(value=java.lang.annotation.RetentionPolicy.RUNTIME)
@java.lang.annotation.Target(value={java.lang.annotation.ElementType.TYPE})
@java.lang.annotation.Inherited
public @interface Namingspace
{
	/**
	 * 命名空间
	 */
	String value();
}
