package com.kyl.ps.interfaces.controller.impl;

import com.kyl.ps.constant.ResponseStatus;
import com.kyl.ps.infrastructure.dao.impl.feedback.FeedbackManagerDao;
import com.kyl.ps.infrastructure.service.impl.area.AreaManagerServiceImpl;
import com.kyl.ps.infrastructure.service.impl.feedback.FeedbackManagerServiceImpl;
import com.kyl.ps.interfaces.controller.AbstractController;
import com.kyl.ps.pojo.BaseInputMessage;
import com.kyl.ps.task.TaskMap;
import com.kyl.ps.util.Constants;
import com.kyl.ps.util.DateUtils;
import com.kyl.ps.util.HttpUtil;
import net.sf.json.JSONObject;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 *
 * Created by Administrator on 2017/2/13 0013.
 */
@Controller
@RequestMapping("/feedbackManager/*")
public class FeedbackManagerController extends AbstractController {
    Logger log = Logger.getLogger(ManagerUserController.class);

    @Autowired
    FeedbackManagerServiceImpl feedbackManagerService;
    @Autowired
    AreaManagerServiceImpl areaManagerService;
    /***
     * @description  getFeedbackInfoList 获取反馈列表
     * @param         request
     * @param         response
     * */
    @RequestMapping("getFeedbackInfoList")
    public void getFeedbackInfoList(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            Map<String,Object>          pageTotalMap    = feedbackManagerService.getFeedbackInfoPageCount(inMessage);
            int                         pageTotal       = ((Long)pageTotalMap.get("pageTotal")).intValue();
            //获取名称是否已经存在 如果存在 则直接提示

            int                         start           = (int)inMessage.getRequestMap().get(Constants.KEY_START);
            int                         mr              = (int)inMessage.getRequestMap().get(Constants.KEY_MAXRESULT);
            inMessage.getRequestMap().put(Constants.KEY_START,Math.abs(start-1)*mr);
            List<Map<String,Object>>    list             = feedbackManagerService.getFeedbackInfoList(inMessage);
            returnMap.put("feedbackList",list);
            int totalPageSize = pageTotal % mr;
            if(totalPageSize == 0 ) returnMap.put("pageTotal",pageTotal/mr);
            else returnMap.put("pageTotal",(pageTotal/mr)+1);
            responseStatus   = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【获取反馈列表返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  getFeedbackInfo 获取反馈内容和回复内容
     * @param         request
     * @param         response
     * */
    @RequestMapping("getFeedbackInfo")
    public void getFeedbackInfo(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            //判断小区名称是否已经存在
            Map<String,Object>       feedbackInfo        = feedbackManagerService.getFeedbackInfo(inMessage);
            returnMap.put("feedbackInfo",feedbackInfo);
            responseStatus   = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【新增/修改区域返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  getFeedbackInfo 回复用户反馈信息 并且发送信息给对应用户
     * @param         request
     * @param         response
     * */
    @RequestMapping("replyFeedbackInfo")
    public void replyFeedbackInfo(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            //判断小区名称是否已经存在
            int      feedbackInfoCount        = feedbackManagerService.replyFeedbackInfo(inMessage);
            //判断积分是否为0, 大于0 将添加到库中积分表中
            if(feedbackInfoCount >0){
                //推送给某一个用户
                Map<String,Object> feedbackInfo  = feedbackManagerService.getFeedbackInfo(inMessage);
                if(feedbackInfo.get("user_id") != null){
                    Map<String,String> params = new HashMap<>();
                    String revert_message = inMessage.getRequestMap().get("revert_content").toString();
                    params.put("content",revert_message);
                    params.put("userid",feedbackInfo.get("user_id").toString());
                    HttpUtil.httpRequestToString(commonConfig.get("server.push.message.url")+"api/message/broadcastuser","POST",params);
                    //添加一条推送消息只服务器
                    inMessage.getRequestMap().clear();
                    String                      sendInformDateTimex        = DateUtils.getCurrentDateTimeSimpleFormat();
                    java.text.SimpleDateFormat  df                  = new SimpleDateFormat("yyyy-MM-dd HH:mm");
                    java.util.Date              ud                  = df.parse(sendInformDateTimex);
                    java.sql.Timestamp          st                  = new java.sql.Timestamp(ud.getTime());
                    inMessage.getRequestMap().put("inform_time",st);
                    inMessage.getRequestMap().put("user_id",feedbackInfo.get("user_id").toString());
                    inMessage.getRequestMap().put("type",1);//1 对某一个用户
                    inMessage.getRequestMap().put("system_content",revert_message);
                    areaManagerService.createSystemPushMessage(inMessage);
                }
            }
            responseStatus   = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【回复用户反馈信息接口】:" + JSONObject.fromObject(returnMap));
    }
}

