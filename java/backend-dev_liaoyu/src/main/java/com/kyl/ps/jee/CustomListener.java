package com.kyl.ps.jee;

import com.kyl.ps.infrastructure.service.impl.area.AreaManagerServiceImpl;
import com.kyl.ps.pojo.BaseInputMessage;
import com.kyl.ps.util.DateUtils;
import org.springframework.web.context.WebApplicationContext;
import org.springframework.web.context.support.WebApplicationContextUtils;

import javax.servlet.ServletContext;
import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;
import java.util.List;
import java.util.Map;

/**
 * Created by Administrator on 2017/2/27 0027.
 */
public class CustomListener implements ServletContextListener {
    @Override
    public void contextInitialized(ServletContextEvent sce) {
        try{
            ServletContext   sc   =  sce.getServletContext();
            WebApplicationContext webApplicationContext  = WebApplicationContextUtils.getWebApplicationContext(sc);
            AreaManagerServiceImpl   areaManagerService   = (AreaManagerServiceImpl)webApplicationContext.getBean("areaManagerServiceImpl");
            initTaskMessage(areaManagerService);
        }catch (Exception e){
            e.printStackTrace();
        }

    }
    private  void initTaskMessage(final  AreaManagerServiceImpl areaManagerService){
        new  Thread(new Runnable() {
            @Override
            public void run() {
                //获取库所有消息,通过获取当前之后的任务信息
                BaseInputMessage inMessage 		= new BaseInputMessage();
                try {
                    inMessage.getRequestMap().put("inform_time", DateUtils.getCurrentDateTimeSimpleFormat());
                    List<Map<String,Object>> list  = areaManagerService.queryAllSystemMessage(inMessage);
                    System.out.println("============恭喜你============获取数据为空==========================="+list.size());
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }
    @Override
    public void contextDestroyed(ServletContextEvent servletContextEvent) {

    }
}
