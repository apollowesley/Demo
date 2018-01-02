package com.kyl.ps.interfaces.controller.impl;

import com.kyl.ps.constant.ResponseStatus;
import com.kyl.ps.infrastructure.service.impl.content.ContentManagerServiceImpl;
import com.kyl.ps.infrastructure.service.impl.material.MaterialManagerServiceImpl;
import com.kyl.ps.interfaces.controller.AbstractController;
import com.kyl.ps.pojo.BaseInputMessage;
import com.kyl.ps.util.Constants;
import com.kyl.ps.util.DateUtils;
import net.sf.json.JSON;
import net.sf.json.JSONArray;
import net.sf.json.JSONObject;
import org.apache.commons.collections.map.HashedMap;
import org.apache.commons.lang.StringEscapeUtils;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.multipart.MultipartHttpServletRequest;
import org.springframework.web.multipart.commons.CommonsMultipartResolver;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.swing.text.AbstractDocument;
import java.io.File;
import java.io.IOException;
import java.net.URLDecoder;
import java.util.*;

/**
 *
 * Created by Administrator on 2017/2/13 0013.
 */
@Controller
@RequestMapping("/contentManager/*")
public class ContentManagerController extends AbstractController {
    Logger log = Logger.getLogger(ManagerUserController.class);

    @Autowired
    ContentManagerServiceImpl contentManagerService;
    /***
     * @description  新增分组
     * @param         request
     * @param         response
     * */
    @RequestMapping("addColumn")
    public void addColumn(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            if(inMessage.getRequestMap().get("column_id") != null){
                contentManagerService.modifyColumn(inMessage);
            }else{
                contentManagerService.addColumn(inMessage);
                returnMap.put("column_id",inMessage.getRequestMap().get("column_id"));
            }
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【新增/修改分组返回接口】:" + JSONObject.fromObject(returnMap));
    }

    /***
     * @description  删除栏目
     * @param         request
     * @param         response
     * */
    @RequestMapping("deleteColumn")
    public void deleteColumn(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            String     deleteColumn = inMessage.getRequestMap().get("column_id").toString();
            //未分组和分组不能删除
            if(inMessage.getRequestMap().get("column_id").equals((Object) 0)||inMessage.getRequestMap().get("column_id").equals((Object) (-1))){
            }else{
                contentManagerService.deleteColumn(inMessage);
                //将内容移动到未分组中
                inMessage.getRequestMap().put("new_column_id",0);//0 为未分组
                contentManagerService.moveColumn(inMessage);
                responseStatus      = ResponseStatus.SUCCESS;
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【删除栏目返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  获取栏目列表
     * @param         request
     * @param         response
     * */
    @RequestMapping("getColumnList")
    public void getColumnList(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus responseStatus  = ResponseStatus.SERVERERROR;
        try {
            //String 							requestParam 		= this.genRequestParam(request);
            //this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            List<Map<String, Object>> list  = contentManagerService.getColumnList();
            returnMap.put("columnList",list);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【获取栏目列表返回接口】:" + JSONObject.fromObject(returnMap));
    }

    /***
     * @description  修改栏目信息
     * @param         request
     * @param         response
     * */
    @RequestMapping("modifyColumn")
    public void modifyColumn(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            if(inMessage.getRequestMap().get("column_id").equals((Object) 0)||inMessage.getRequestMap().get("column_id").equals((Object) (-1))){
            }else {
                contentManagerService.modifyColumn(inMessage);
                responseStatus      = ResponseStatus.SUCCESS;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【 修改栏目信息返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  修改栏目排序
     * @param         request
     * @param         response
     * */
    @RequestMapping("modifyColumnOrder")
    public void modifyColumnOrder(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            String                          column_json_arr_str = inMessage.getRequestMap().get("column_values").toString();
            JSONArray                       columnJsonArr       =  JSONArray.fromObject(column_json_arr_str);
            inMessage.getRequestMap().put("columnList",columnJsonArr);
            contentManagerService.modifyColumnOrder(inMessage);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【修改栏目排序返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  内容发布
     * @param         request
     * @param         response
     * */
    @RequestMapping("addOrModifyContentInfo")
    public void createContentInfo(HttpServletRequest request
            ,HttpServletResponse response,@RequestParam Map<String,Object> map ,@RequestParam("article_content") String  article_content  ) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            inMessage.setRequestMap(map);
            String   mytext2   =   article_content;
            inMessage.getRequestMap().put("article_content",mytext2);
            int  status    =  -1;
            if(inMessage.getRequestMap().get("article_id") != null){
                status    = contentManagerService.modifyContentInfo(inMessage);
            }else{
                int         read_random    = new Random().nextInt(700);//取300以内到1000以下
                             inMessage.getRequestMap().put("read_random",read_random+300);
                             status         = contentManagerService.addContentInfo(inMessage);
            }
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【内容发布返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  获取内容列表
     * @param         request
     * @param         response
     * */
    @RequestMapping("getColumnContentListInfo")
    public void getColumnContentListInfo(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            //获取栏目列表
            if(inMessage.getRequestMap().get("column_id")!=null){//获取某一个栏目内容
                Map<String, Object>         map     = new HashedMap();
                getColumnContent(inMessage,map,request);
                returnMap.put("columnList",map);
            }else{//获取全部栏目
                    List<Map<String, Object>> list  = contentManagerService.getColumnList();
                    if(list.size() ==1){//只有第一条时 为未分组
                            inMessage.getRequestMap().put("column_id",list.get(0).get("column_id"));
                            inMessage.getRequestMap().put(Constants.KEY_START,1);//初始化一次
                            getColumnContent(inMessage,list.get(0),request);
                    }else{//会取第二个 因为当不止条栏目时 第一个的未分组会排在最后 所以取第二个
                            inMessage.getRequestMap().put("column_id",list.get(1).get("column_id"));
                            inMessage.getRequestMap().put(Constants.KEY_START,1);//初始化一次
                            getColumnContent(inMessage,list.get(1),request);
                    }
                    returnMap.put("columnList",list);
                /***
                returnMap.put("columnList",list);
                for(Map<String, Object> map:list){
                    inMessage.getRequestMap().put("column_id",map.get("column_id"));
                    inMessage.getRequestMap().put(Constants.KEY_START,1);//初始化一次
                    getColumnContent(inMessage,map,request);

                    System.out.println("====执行了几次==="+JSONObject.fromObject(map).toString());
                    break;
                }
                returnMap.put("columnList",list);
                 ***/
            }
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【内容发布返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  获取内容详情
     * @param         request
     * @param         response
     * */
    @RequestMapping("getColumnArticleByArticleId")
    public void getColumnArticleByArticleId(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            //获取栏目列表
            Map<String,Object>  mapInfo =  contentManagerService.getColumnArticleByArticleId(inMessage);
            mapInfo.put("article_img_path",commonConfig.get("server.img.url"));
            //找出img的地方 进行拼接图片
            String  articleContent   =  mapInfo.get("article_content").toString();
                    articleContent   = articleContent.replaceAll("<img src=\"","<img src=\""+commonConfig.get("server.img.url"));

            mapInfo.put("article_content",articleContent);
            mapInfo.put("article_img_url",mapInfo.get("article_img_url").toString());
            returnMap.put("articleInfo",mapInfo);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【内容发布返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  删除内容
     * @param         request
     * @param         response
     * */
    @RequestMapping("deleteArticle")
    public void deleteArticle(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            //获取栏目列表
            contentManagerService.deleteArticle(inMessage);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【删除内容返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  置顶内容
     * @param         request
     * @param         response
     * */
    @RequestMapping("stickArticle")
    public void stickArticle(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            //获取栏目列表
            contentManagerService.stickArticle(inMessage);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【置顶内容返回接口】:" + JSONObject.fromObject(returnMap));
    }
    private void getColumnContent(BaseInputMessage inMessage,Map<String, Object> returnMap,HttpServletRequest request){
        //返回最新数据给客户端
        Map<String,Object>          pageTotalMap    = contentManagerService.getColumnContentCountByColumnId(inMessage);
        int                         pageTotal       = ((Long)pageTotalMap.get("pageTotal")).intValue();
        //获取名称是否已经存在 如果存在 则直接提示

        int                         start           = (int)inMessage.getRequestMap().get(Constants.KEY_START);
        int                         mr              = (int)inMessage.getRequestMap().get(Constants.KEY_MAXRESULT);
        inMessage.getRequestMap().put(Constants.KEY_START,Math.abs(start-1)*mr);
        List<Map<String,Object>>    list             = contentManagerService.getColumnContentByColumnId(inMessage);
        returnMap.put("contentList",list);
        int totalPageSize = pageTotal % mr;
        if(totalPageSize == 0 ) returnMap.put("pageTotal",pageTotal/mr);
        else returnMap.put("pageTotal",(pageTotal/mr)+1);
    }
}
