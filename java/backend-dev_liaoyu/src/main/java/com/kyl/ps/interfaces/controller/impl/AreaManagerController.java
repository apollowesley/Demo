package com.kyl.ps.interfaces.controller.impl;

import com.kyl.ps.constant.ResponseStatus;
import com.kyl.ps.infrastructure.service.impl.area.AreaManagerServiceImpl;
import com.kyl.ps.infrastructure.service.impl.content.ContentManagerServiceImpl;
import com.kyl.ps.interfaces.controller.AbstractController;
import com.kyl.ps.pojo.BaseInputMessage;
import com.kyl.ps.task.TaskMap;
import com.kyl.ps.util.Constants;
import com.kyl.ps.util.DateUtils;
import com.kyl.ps.util.HttpUtil;
import net.sf.json.JSONArray;
import net.sf.json.JSONObject;
import org.apache.commons.collections.map.HashedMap;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

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
@RequestMapping("/areaManager/*")
public class AreaManagerController extends AbstractController {
    Logger log = Logger.getLogger(ManagerUserController.class);

    @Autowired
    AreaManagerServiceImpl areaManagerService;
    @Autowired
    TaskMap taskMap;
    /***
     * @description  getUserAreaList 获取用户创建区域列表
     * @param         request
     * @param         response
     * */
    @RequestMapping("getUserAreaList")
    public void getUserAreaList(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            Object   obj = inMessage.getRequestMap().get("area_type");
            List<Map<String,Object>>  list   = null ;
            System.out.println("===obj=="+obj);
            if(obj == null || "".equals(obj)||"0".equals(obj.toString())){//省
                list  = areaManagerService.getUserAreaList(inMessage);
            }else if(obj != null && obj.toString().equals("1")){//市
                list = areaManagerService.getCityUserAreaList(inMessage);
            }else if(obj != null && obj.toString().equals("2")){//县
                list = areaManagerService.getDistUserAreaList(inMessage);
            }
            returnMap.put("list",list);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【新增/修改分组返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  addUserArea 新增区域
     * @param         request
     * @param         response
     * */
    @RequestMapping("addUserArea")
    public void addUserArea(HttpServletRequest request
            ,HttpServletResponse response,@RequestParam Map<String,Object> paramMap) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus responseStatus  = ResponseStatus.SERVERERROR;
        try {
//            String 							requestParam 		= this.genRequestParam(request);
//            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));.
            inMessage.setRequestMap(paramMap);
            //判断小区名称是否已经存在
            Map<String,Object>       map             = areaManagerService.getUserAreaPlot(inMessage);
            Object                oldPlotObjId       = inMessage.getRequestMap().get("plot_id");
            String                oldObjId           = null;
            String                newObjId           = null;
            oldPlotObjId    =  oldPlotObjId == null ? "0":oldPlotObjId.toString();
            if(map  != null){
                Object  newGardenObjID          =  map.get("garden_id");
                        newObjId                =  newGardenObjID == null ? "0":newGardenObjID.toString();
                System.out.println("newObjId.equals(oldPlotObjId)\")==="+newObjId.equals(oldPlotObjId));

                if(newObjId.equals(oldPlotObjId)){
                    int                      status             = areaManagerService.addUserAreaPlot(inMessage);
                                             responseStatus      = ResponseStatus.SUCCESS;
                }else{
                    responseStatus         = ResponseStatus.NAMEALREADYEXISTS;
                }
            }else{
                int                      status   = areaManagerService.addUserAreaPlot(inMessage);
                if(status >0){
                    responseStatus      = ResponseStatus.SUCCESS;
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【新增/修改区域返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  getProvinceList 获取省市县列表
     * @param         request
     * @param         response
     * */
    @RequestMapping("getAreaList")
    public void getAreaList(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            if(null == requestParam || "".equals(requestParam)){
                requestParam = "{area_id:0}";//如果在获取时 传值 则默认为获取省份信息
            }
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            //判断小区名称是否已经存在
            List<Map<String,Object>>  list   = areaManagerService.getAreaList(inMessage);
            returnMap.put("areaList",list);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【获取省返回接口】:" + JSONObject.fromObject(returnMap));
    }

    /***
     * @description  getPlotListByAreaId 获取小区列表名称
     * @param         request
     * @param         response
     * */
    @RequestMapping("getPlotListByAreaId")
    public void getPlotListByAreaId(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            //判断小区名称是否已经存在
            List<Map<String,Object>>  list       = areaManagerService.getPlotListByAreaId(inMessage);
            for(Map<String,Object>  map : list){
                String url = commonConfig.get("server.img.url");
                String plot_photo = url+map.get("photo").toString();
                map.put("photo_url",url);
            }
            returnMap.put("plotList",list);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【获取小区列表名称返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  getPlotListByAreaId 获取小区列表名称
     * @param         request
     * @param         response
     * */
    @RequestMapping("deletePlot")
    public void deletePlot(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            //判断小区名称是否已经存在
            int  status       = areaManagerService.deletePlot(inMessage);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【获取小区列表名称返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  getSystemPushMessageList 获取推送列表信息
     * @param         request
     * @param         response
     * */
    @RequestMapping("getSystemPushMessageList")
    public void getSystemMessageList(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            Map<String,Object> pageTotalMap  = areaManagerService.getSystemPushMessageListCount(inMessage);
            int                pageTotal     = ((Long)pageTotalMap.get("pageTotal")).intValue();
            //获取名称是否已经存在 如果存在 则直接提示
            int              start        = (int)inMessage.getRequestMap().get(Constants.KEY_START);
            int              mr           = (int)inMessage.getRequestMap().get(Constants.KEY_MAXRESULT);
            inMessage.getRequestMap().put(Constants.KEY_START,(start-1)*mr);

            //判断小区名称是否已经存在
            List<Map<String,Object>>  list          = areaManagerService.getSystemPushMessageList(inMessage);

            int                     totalPageSize   = pageTotal % mr;
            if(totalPageSize == 0 ) returnMap.put("pageTotal",pageTotal/mr);
            else returnMap.put("pageTotal",(pageTotal/mr)+1);
            returnMap.put("pushMessageList",list);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【消息推送列表返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  createSystemPushMessage 添加系统推送信息
     * @param         request
     * @param         response
     * */
    @RequestMapping("createSystemPushMessage")
    public void createSystemPushMessage(HttpServletRequest request
            ,HttpServletResponse response,@RequestParam Map<String,Object> map) throws  Exception{
       final BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus responseStatus  = ResponseStatus.SERVERERROR;
        try {
            inMessage.setRequestMap(map);
            //将日期字符串转成数据库能识别的日期类型
            Object                      inforObj                    = inMessage.getRequestMap().get("inform_time");
             String                      sendInformDateTimex        = DateUtils.getCurrentDateTimeSimpleFormat();
            if(inforObj == null || "".equals(inforObj)){
            }else{
                                         sendInformDateTimex        = inforObj.toString();
            }

            final String                      sendInformDateTime  = sendInformDateTimex;
            java.text.SimpleDateFormat  df                  = new SimpleDateFormat("yyyy-MM-dd HH:mm");
            java.util.Date              ud                  = df.parse(sendInformDateTime);
            java.sql.Timestamp          st                  = new java.sql.Timestamp(ud.getTime());
            String                      sendContent         = inMessage.getRequestMap().get("system_content").toString();
            inMessage.getRequestMap().put("inform_time",st);
            Pattern p_html              = Pattern.compile("<[^>]+>",Pattern.CASE_INSENSITIVE);
            Matcher m_html              = p_html.matcher(sendContent);
                    sendContent         = m_html.replaceAll(""); //过滤html标签
            inMessage.getRequestMap().put("system_content",sendContent);
            inMessage.getRequestMap().put("type",2);//群发
            int                             status               = areaManagerService.createSystemPushMessage(inMessage);
            if(status > 0 ){
                //*******向定时器发送一条消息******/
                taskMap.put(new Runnable() {
                    @Override
                    public void run() {
                            System.out.println("恭喜你!你已经成功添加一条!内容为:"+inMessage.getRequestMap().get("system_content")+",执行时间:"+sendInformDateTime);
                            Map<String,String> params = new HashMap<>();
                            params.put("content",inMessage.getRequestMap().get("system_content").toString());
                            HttpUtil.httpRequestToString(commonConfig.get("server.push.message.url")+"api/message/allbroadcast","POST",params);
                    }
                },ud);
            }
                  responseStatus       = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【createSystemPushMessage】:" + JSONObject.fromObject(returnMap));
    }
}

