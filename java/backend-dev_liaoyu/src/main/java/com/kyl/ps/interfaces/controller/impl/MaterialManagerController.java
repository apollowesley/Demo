package com.kyl.ps.interfaces.controller.impl;

import com.kyl.ps.constant.ResponseStatus;
import com.kyl.ps.infrastructure.service.impl.manageruser.ManagerUserServiceImpl;
import com.kyl.ps.infrastructure.service.impl.material.MaterialManagerServiceImpl;
import com.kyl.ps.interfaces.controller.AbstractController;
import com.kyl.ps.pojo.BaseInputMessage;
import com.kyl.ps.util.Constants;
import com.kyl.ps.util.DateUtils;
import com.kyl.ps.util.FileUtil;
import net.sf.json.JSONArray;
import net.sf.json.JSONObject;
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
import java.io.File;
import java.io.IOException;
import java.util.*;

/**
 *素材管理
 * Created by Administrator on 2017/2/13 0013.
 */
@Controller
@RequestMapping("/materialManager/*")
public class MaterialManagerController extends AbstractController {
    Logger log = Logger.getLogger(ManagerUserController.class);
    @Autowired
    MaterialManagerServiceImpl materialService;
    @RequestMapping("springUpload")
    public void  springUpload(HttpServletRequest request,HttpServletResponse response,@RequestParam(value="category_id") String categoryID  ) throws Exception
    {
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus            responseStatus  = ResponseStatus.SERVERERROR;
        try {
            inMessage.getRequestMap().put("create_time", DateUtils.getCurrentDateTimeSimpleFormat());
            if(categoryID == null || "-1".equals(categoryID)){//如过没有 则默认是未添加到分组中 category_id=-1
                categoryID = "-1";
            }
            inMessage.getRequestMap().put("category_id", categoryID);
            inMessage.getRequestMap().put("update_time", DateUtils.getCurrentDateTimeSimpleFormat());
            List<JSONObject> uploadPathArr  =  upload(request,categoryID);

            inMessage.getRequestMap().put("pathList",uploadPathArr);
            //获取名称是否已经存在 如果存在 则直接提示
            int  i = materialService.saveMaterialInfo(inMessage);
             if(i > 0 ){
                 responseStatus      = ResponseStatus.SUCCESS;
             }
        } catch (Exception e) {
            e.printStackTrace();
            returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
            returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【新增/修改分组返回接口】:" + JSONObject.fromObject(returnMap));
    }

    private List<JSONObject> upload(HttpServletRequest request, String categoryID )throws Exception {
        System.out.println("+=categoryID="+categoryID);
        List<JSONObject>  sb = new ArrayList<JSONObject> ();
        long  startTime=System.currentTimeMillis();
        //将当前上下文初始化给  CommonsMutipartResolver （多部分解析器）
        CommonsMultipartResolver multipartResolver=new CommonsMultipartResolver(
                request.getSession().getServletContext());
        //检查form中是否有enctype="multipart/form-data"
        if(multipartResolver.isMultipart(request))
        {
            //将request变成多部分request
            MultipartHttpServletRequest multiRequest=(MultipartHttpServletRequest)request;
            //获取multiRequest 中所有的文件名
            Iterator iter=multiRequest.getFileNames();
            while(iter.hasNext())
            {
                //一次遍历所有文件
                MultipartFile file=multiRequest.getFile(iter.next().toString());
                if(file!=null)
                {
                    JSONObject  jsonObject      = new JSONObject();
                    String      rootPath          = FileUtil.getWebAppRealPath();
                    String      tempFileName     = file.getOriginalFilename();
                    String      suffix           = tempFileName.substring(tempFileName.lastIndexOf("."),tempFileName.length());
                    String      fileNamePath     = File.separator+"upload"+File.separator+"material"+File.separator+categoryID+File.separator;
                    FileUtil.createDir(rootPath+fileNamePath);
                    String  fileNameName     = File.separator+"upload"+File.separator+"material"+File.separator+categoryID+File.separator+UUID.randomUUID()+suffix;
                    String  savePath         = rootPath + fileNameName;
                    //上传
                    file.transferTo(new File(savePath));
                    fileNameName = fileNameName.replaceAll("\\\\","/");
                    jsonObject.put("material_name",tempFileName);
                    jsonObject.put("material_url",fileNameName);
                    sb.add(jsonObject);
                }
            }

        }
        long  endTime=System.currentTimeMillis();
        System.out.println("方法三的运行时间："+String.valueOf(endTime-startTime)+"ms");
        return sb;
    }
  /***
   * @description  新增分组
   * @param         request
   * @param         response
   * */
  @RequestMapping("addCategory")
  public void addCategory(HttpServletRequest request
          ,HttpServletResponse response) throws  Exception{
      BaseInputMessage 			inMessage 		= new BaseInputMessage();
      Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
      ResponseStatus            responseStatus  = ResponseStatus.SERVERERROR;
      try {
          String 							requestParam 		= this.genRequestParam(request);
          this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
          inMessage.getRequestMap().put("create_time", DateUtils.getCurrentDateTimeSimpleFormat());
          Object  category_id = inMessage.getRequestMap().get("category_id");

          //获取名称是否已经存在 如果存在 则直接提示
          Map<String,Object>  count = materialService.queryCategoryName(inMessage);
          if(count != null){
              responseStatus      = ResponseStatus.NAMEALREADYEXISTS;
          }else{
              if(category_id != null){//修改
                  int  status = materialService.modifyCategory(inMessage);
              }else{//新增
                  int  return_category_id = materialService.addCategory(inMessage);
                  count = materialService.queryCategoryName(inMessage);
                  returnMap.put("material_save_path","upload/material/"+"material_"+return_category_id+"/");
                  returnMap.put("category_id",inMessage.getRequestMap().get("category_id"));
              }
              responseStatus      = ResponseStatus.SUCCESS;
          }
      } catch (Exception e) {
          e.printStackTrace();
          returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
          returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
      }
      writeResponseStatus(responseStatus,returnMap,response);
      // 返回数据
      log.info("【新增/修改分组返回接口】:" + JSONObject.fromObject(returnMap));
  }
    /***
     * @description  修改分组【重命名分组】
     * @param         request
     * @param         response
     * */
    @RequestMapping("modifyCategory")
    public void modifyCategory(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            //获取名称是否已经存在 如果存在 则直接提示
            int  status = materialService.modifyCategory(inMessage);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
            returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
            returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【修改分组返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  删除分组
     * @param         request
     * @param         response
     * */
    @RequestMapping("deleteCategory")
    public void deleteCategory(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            //获取名称是否已经存在 如果存在 则直接提示
            int    category_id = (int)inMessage.getRequestMap().get("category_id");
            switch (category_id){
                case 0://全部
                case -1:{//未分组不能进行删除
                    break;
                }
                default:{
                    //将本组中的数据移植到未分组中
                    inMessage.getRequestMap().put("new_category_id",-1);
                    materialService.moveCategory(inMessage);
                    int  status = materialService.deleteCategory(inMessage);
                }
            }
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
            returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
            returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【删除分组返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  获取分组列表 获取出每组中素材数量
     * @param         request
     * @param         response
     * */
    @RequestMapping("getCategoryList")
    public void getCategoryList(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            //String 							requestParam 		= this.genRequestParam(request);
            //this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            //获取名称是否已经存在 如果存在 则直接提示
            List<Map<String,Object>>  list   = materialService.getCategoryList(inMessage);
            for(Map<String,Object>   map :list){
                map.put("material_save_path","upload/material/"+"material_"+map.get("category_id")+"/");
            }
            returnMap.put("categoryList",list);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
            returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
            returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【获取分组列表返回接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  根据分组编号 获取分组中素材列表
     * @param         request
     * @param         response
     * */
    @RequestMapping("getMaterialListByCategoryId")
    public void getMaterialListByCategoryId(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            //获取总页数
            Map<String,Object> pageTotalMap  = materialService.getMaterialCountByCategoryId(inMessage);
            int                pageTotal     = ((Long)pageTotalMap.get("pageTotal")).intValue();
            //获取名称是否已经存在 如果存在 则直接提示
            int              start        = (int)inMessage.getRequestMap().get(Constants.KEY_START);
            int              mr           = (int)inMessage.getRequestMap().get(Constants.KEY_MAXRESULT);
            inMessage.getRequestMap().put(Constants.KEY_START,(start-1)*mr);
            List<Map<String,Object>>  list = materialService.getMaterialListByCategoryId(inMessage);
            for(Map<String,Object> item:list){
                String  url             = request.getServletContext().getContextPath();
                item.put("material_path",commonConfig.get("server.img.url"));
                item.put("material_url",item.get("material_url"));
            }
            int totalPageSize = pageTotal % mr;
            if(totalPageSize == 0 ) returnMap.put("pageTotal",pageTotal/mr);
            else returnMap.put("pageTotal",(pageTotal/mr)+1);
            returnMap.put("materialList",list);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
            returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
            returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【根据分组编号 获取分组中素材列表接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  移动素材
     * @param         request
     * @param         response
     * */
    @RequestMapping("moveMaterialCategory")
    public void moveMaterialCategory(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            inMessage.getRequestMap().put("materialIdList",inMessage.getRequestMap().get("material_id_values").toString().split(","));
            materialService.moveCategoryBatch(inMessage);
            getNewMaterialData(inMessage,returnMap,request);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
            returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
            returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【移动素材接口】:" + JSONObject.fromObject(returnMap));
    }
    /***
     * @description  删除素材
     * @param         request
     * @param         response
     * */
    @RequestMapping("deleteMaterial")
    public void deleteMaterial(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            String                          material_url        = inMessage.getRequestMap().get("material_url").toString();
            String                          rootPath            = FileUtil.getWebAppRealPath();
            File                            file                = new File(rootPath+material_url);
            //去掉material_url?后面的参数
           // material_url    =  material_url.substring(0,material_url.lastIndexOf("?"));
            //删除本地图片
            //materialService.deleteMaterial(inMessage);
            //删除OSS文件
            FileUtil.deleteOSSFile(material_url);
            if(file.isFile()){
                file.delete();
            }
            getNewMaterialData(inMessage,returnMap,request);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
            returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
            returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【删除素材接口】:" + JSONObject.fromObject(returnMap));
    }

    private  void getNewMaterialData(BaseInputMessage inMessage,Map<String, Object> returnMap,HttpServletRequest request){
        //返回最新数据给客户端
        Map<String,Object> pageTotalMap  = materialService.getMaterialCountByCategoryId(inMessage);
        int                pageTotal     = ((Long)pageTotalMap.get("pageTotal")).intValue();
        //获取名称是否已经存在 如果存在 则直接提示
        int              start        = (int)inMessage.getRequestMap().get(Constants.KEY_START);
        int              mr           = (int)inMessage.getRequestMap().get(Constants.KEY_MAXRESULT);
        inMessage.getRequestMap().put(Constants.KEY_START,(start-1)*mr);
        List<Map<String,Object>>  list = materialService.getMaterialListByCategoryId(inMessage);
        //判断是否当前页内容是否还存在值 并且也不是页 递减一页在获取数据
        if(list.size() == 0 && pageTotal != 0){
            inMessage.getRequestMap().put(Constants.KEY_START,(start-2)*mr);
            list = materialService.getMaterialListByCategoryId(inMessage);
        }
        for(Map<String,Object> item:list){
            String  url             = commonConfig.get("server.img.url");
            String material_urlx     = item.get("material_url").toString();
            item.put("material_path",url);
            item.put("material_url",material_urlx);
        }
        int totalPageSize = pageTotal % mr;
        if(totalPageSize == 0 ) returnMap.put("pageTotal",pageTotal/mr);
        else returnMap.put("pageTotal",(pageTotal/mr)+1);
        returnMap.put("materialList",list);
    }
    /***
     * @description  移动素材
     * @param         request
     * @param         response
     * */
    @RequestMapping("modifyMaterial")
    public void modifyMaterial(HttpServletRequest request
            ,HttpServletResponse response) throws  Exception{
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            materialService.modifyMaterial(inMessage);
            responseStatus      = ResponseStatus.SUCCESS;
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【移动素材接口】:" + JSONObject.fromObject(returnMap));
    }
    //新增素材
    @RequestMapping("createMaterial")
    public void  createMaterial(HttpServletRequest request,HttpServletResponse response) throws Exception
    {
        BaseInputMessage 			inMessage 		= new BaseInputMessage();
        Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
        ResponseStatus            responseStatus  = ResponseStatus.SERVERERROR;
        try {
            String 							requestParam 		= this.genRequestParam(request);
            this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
            inMessage.getRequestMap().put("create_time", DateUtils.getCurrentDateTimeSimpleFormat());
            String   categoryID  = inMessage.getRequestMap().get("category_id").toString();
            if(categoryID == null || "-1".equals(categoryID)){//如过没有 则默认是未添加到分组中 category_id=-1
                categoryID = "-1";
            }
            inMessage.getRequestMap().put("category_id", categoryID);

            inMessage.getRequestMap().put("update_time", DateUtils.getCurrentDateTimeSimpleFormat());
            String  materialPaths = inMessage.getRequestMap().get("material_path_arr").toString();
            JSONArray uploadPathArr  =  JSONArray.fromObject(materialPaths);

            inMessage.getRequestMap().put("pathList",uploadPathArr);
            //获取名称是否已经存在 如果存在 则直接提示
            int  i = materialService.saveMaterialInfo(inMessage);
            if(i > 0 ){
                responseStatus      = ResponseStatus.SUCCESS;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        writeResponseStatus(responseStatus,returnMap,response);
        // 返回数据
        log.info("【新增/修改分组返回接口】:" + JSONObject.fromObject(returnMap));

    }
}
