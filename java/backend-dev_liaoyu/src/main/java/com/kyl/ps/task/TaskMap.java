package com.kyl.ps.task;

import com.aliyun.oss.common.utils.DateUtil;
import com.kyl.ps.infrastructure.dao.impl.area.AreaManagerDao;
import com.kyl.ps.infrastructure.service.impl.area.AreaManagerServiceImpl;
import com.kyl.ps.interfaces.controller.impl.ManagerUserController;
import com.kyl.ps.pojo.BaseInputMessage;
import com.kyl.ps.util.BeanHolder;
import com.kyl.ps.util.DateUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.Trigger;
import org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler;
import org.springframework.stereotype.Service;

import javax.xml.ws.Holder;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

@Service
public class TaskMap {
    public ThreadPoolTaskScheduler getTaskScheduler() {
        return taskScheduler;
    }

    public void setTaskScheduler(ThreadPoolTaskScheduler taskScheduler) {
        this.taskScheduler = taskScheduler;
    }


    private ThreadPoolTaskScheduler taskScheduler = new ThreadPoolTaskScheduler();
    @Autowired
    BeanHolder beanHolder;
    org.apache.log4j.Logger log = org.apache.log4j.Logger.getLogger(TaskMap.class);
    public TaskMap() {
        log.info("init TaskMap ");
        init();
    }
    private void init(){
        taskScheduler.setPoolSize(10);
        taskScheduler.initialize();

    }
   public  void put(Runnable task,Object obj){
        if(obj instanceof  Date){
            taskScheduler.schedule(task,(Date)obj);
        }else if(obj instanceof Trigger){
            taskScheduler.schedule(task,(Trigger)obj);
        }

   }
}
