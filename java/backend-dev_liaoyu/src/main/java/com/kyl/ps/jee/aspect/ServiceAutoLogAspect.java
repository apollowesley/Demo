package com.kyl.ps.jee.aspect;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.springframework.core.annotation.Order;

import com.kyl.ps.infrastructure.dao.DataSourceInstances;
import com.kyl.ps.infrastructure.dao.DataSourceSwitch;

/**
 * @author BoZhang
 *
 */
@Aspect
public class ServiceAutoLogAspect {

	@Order(value = 1)
	@Pointcut("execution(public * com.kyl.ps.*.service.*.*(..))") 
	public void serviceAOP(){}
	
	@Around("serviceAOP()")
	public Object serviceAround(ProceedingJoinPoint joinPoint) throws Throwable
	{
		Object ret = null;
		StringBuilder logMessageBuilder = null;
		
		final Log  logger = LogFactory.getLog(joinPoint.getTarget().getClass());
		
		try
		{
			//切换数据源
			if (joinPoint.getTarget().toString().contains("userdb")) {
				DataSourceSwitch.setDataSourceType(DataSourceInstances.MYSQL_USERDB); 
			} else {
				DataSourceSwitch.setDataSourceType(DataSourceInstances.MYSQL_DEFAULT); 
			}
			
			if (logger.isDebugEnabled())
			{
				logMessageBuilder = new StringBuilder();
				logMessageBuilder.append("Service layer Auto INFO Log \r\n{\r\n");
				logMessageBuilder.append("className:");
				logMessageBuilder.append(joinPoint.getTarget());
				logMessageBuilder.append("\r\nmethodName:");
				logMessageBuilder.append(joinPoint.getSignature().toShortString());
				Object[] args = joinPoint.getArgs();
				if (null != args)
				{
					for (int i = 0; i < args.length; i++)
					{
						logMessageBuilder.append("\r\nparam_");
						logMessageBuilder.append(i);
						if (null == args[i])
						{
							logMessageBuilder.append(" is ");
							logMessageBuilder.append("null");
						}
						else
						{
							logMessageBuilder.append(":");
							logMessageBuilder.append(args[i]);
						}
					}
				}
				
				logMessageBuilder.append("\r\n}");
			}

			ret = joinPoint.proceed();

//			if (logger.isDebugEnabled() && null != logMessageBuilder)
//			{
//				logMessageBuilder.append("\r\nresult:");
//				logMessageBuilder.append(ret);
//				logMessageBuilder.append("\r\n}");
//			}
			return ret;
		}
		catch (Throwable ex)
		{
			if (logger.isDebugEnabled() && null != logMessageBuilder)
			{
				logMessageBuilder.append(" | exception:");
				logMessageBuilder.append(ex.toString() + "#" + ex.getMessage());
				logMessageBuilder.append("}");
			}
			throw ex;
		}finally{
			if(logger.isDebugEnabled() && null != logMessageBuilder){
				logger.info(logMessageBuilder.toString());
			}
		}
	}
}
