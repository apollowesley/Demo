package com.kyl.ps.interfaces.controller;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.util.*;
import java.util.zip.GZIPOutputStream;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import com.kyl.ps.constant.ResponseStatus;
import net.sf.json.JSONObject;

import org.apache.commons.lang.StringUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.servlet.ModelAndView;

import com.kyl.ps.exception.DBException;
import com.kyl.ps.exception.ExceptionCode;
import com.kyl.ps.exception.GenerateHtmlException;
import com.kyl.ps.exception.JSONException;
import com.kyl.ps.exception.NotDataException;
import com.kyl.ps.exception.NotEnoughPrivilegeException;
import com.kyl.ps.exception.NotLoginException;
import com.kyl.ps.infrastructure.dao.mybatis.Page;
import com.kyl.ps.infrastructure.service.impl.customer.CustomerServiceImpl;
import com.kyl.ps.infrastructure.service.impl.dict.DictServiceImpl;
import com.kyl.ps.infrastructure.service.impl.manageruser.ManagerUserServiceImpl;
import com.kyl.ps.infrastructure.service.impl.recycler.RecyclerServiceImpl;
import com.kyl.ps.infrastructure.service.impl.sticker.StickerServiceImpl;
import com.kyl.ps.jee.JEEConstant;
import com.kyl.ps.pojo.BaseInputMessage;
import com.kyl.ps.pojo.BaseReturnMessage;
import com.kyl.ps.pojo.MsgHelper;
import com.kyl.ps.util.Constants;
import com.kyl.ps.util.DateUtils;
//import com.kyl.ps.util.JsonConvertor;

/**
 * 
 * <p>
 * Title: AbstractController
 * </p>
 * <p>
 * Description: com.soarsky.ps.controller
 * </p>
 * <p>
 * Copyright: Copyright (c) 2013
 * </p>
 * <p>
 * Company: Kyn
 * </p>
 * 
 * @author Jason.Guo
 * @date
 */
@SuppressWarnings({ "rawtypes", "unchecked" })
public abstract class AbstractController implements JEEConstant {

    Log        logger = LogFactory.getLog(AbstractController.class);
    protected  String  defaultResize ="?x-oss-process=image/resize,m_fixed,h_100,w_100";
    public Map parameterMap;
    @Autowired
    private ManagerUserServiceImpl managerUserServiceImpl;
    @Autowired
    private CustomerServiceImpl customerServiceImpl;
    @Autowired
    private DictServiceImpl dictServiceImpl;
    @Autowired
    private RecyclerServiceImpl recyclerServiceImpl;
    @Autowired
    private StickerServiceImpl stickerServiceImpl;
    
    
    
    // 管理员信息map
    static public Map<String, Map<String,Object>> MANAGER_USER = new HashMap<String, Map<String,Object>>();
    // 用户信息map
    static public Map<String, Map<String,Object>> USER_ACCOUNT = new HashMap<String, Map<String,Object>>();
    // 用户扩展信息map
    static public Map<String, Map<String,Object>> USER_EXTEND = new HashMap<String, Map<String,Object>>();
    // 小区信息map
    static public Map<String, Map<String,Object>> DICT_GARDEN = new HashMap<String, Map<String,Object>>();
    // 回收人员信息map
    static public Map<String, Map<String,Object>> RECYCLER = new HashMap<String, Map<String,Object>>();
    // 贴纸印刷批次map
    static public Map<String, Map<String,Object>> CREATIONS = new HashMap<String, Map<String,Object>>();
    //配置文件信息
    static public Map<String,String> commonConfig = new HashMap<String, String>();
    
    static {
        Properties prop =  new  Properties();
        InputStream in = AbstractController. class .getResourceAsStream( "/properties/common.properties" );
        try  {
            prop.load(in);
            Iterator<String> it=prop.stringPropertyNames().iterator();
            while(it.hasNext()){
                String key  =   it.next();
                commonConfig.put(key,prop.getProperty(key));
                System.out.println(key+":"+prop.getProperty(key));
            }
            in.close();
        }  catch  (IOException e) {
            e.printStackTrace();
            System.out.println("初始化配置文件失败;");
        }
    }
    public	Map<String, Map<String,Object>> loadAllManagerUser(BaseInputMessage inMessage){
    	if(MANAGER_USER.size() == 0){
    		List<Map<String,Object>> managerUsers = managerUserServiceImpl.queryAllManagerUser(inMessage);
    		for (Map<String, Object> map : managerUsers) {
    			MANAGER_USER.put(map.get("account_id").toString(), map);
    		}
    		return MANAGER_USER;
    	}else{
    		return MANAGER_USER;
    	}
    }
    
    
    public	Map<String, Map<String,Object>> loadAllUserAccount(BaseInputMessage inMessage){
    	if(USER_ACCOUNT.size() == 0){
    		List<Map<String,Object>> users = customerServiceImpl.queryAllUser(inMessage);
    		for (Map<String, Object> map : users) {
    			USER_ACCOUNT.put(map.get("user_id").toString(), map);
    		}
    		return USER_ACCOUNT;
    	}else{
    		return USER_ACCOUNT;
    	}
    }
    
    
    public	Map<String, Map<String,Object>> loadAllUserExtend(BaseInputMessage inMessage){
    	if(USER_EXTEND.size() == 0){
    		List<Map<String,Object>> userextends = customerServiceImpl.queryAllUserExtend(inMessage);
    		for (Map<String, Object> map : userextends) {
    			USER_EXTEND.put(map.get("user_id").toString(), map);
    		}
    		return USER_EXTEND;
    	}else{
    		return USER_EXTEND;
    	}
    }
    
    
    public	Map<String, Map<String,Object>> loadAllDictGaeden(BaseInputMessage inMessage){
    	if(DICT_GARDEN.size() == 0){
    		List<Map<String,Object>> gaedens = dictServiceImpl.queryGaedens(inMessage);
    		for (Map<String, Object> map : gaedens) {
    			DICT_GARDEN.put(map.get("garden_id").toString(), map);
    		}
    		return DICT_GARDEN;
    	}else{
    		return DICT_GARDEN;
    	}
    }
    
    public	Map<String, Map<String,Object>> loadAllRecycler(BaseInputMessage inMessage){
    	if(RECYCLER.size() == 0){
    		List<Map<String,Object>> recyclers = recyclerServiceImpl.queryAllRecycles(inMessage);
    		for (Map<String, Object> map : recyclers) {
    			RECYCLER.put(map.get("recycler_id").toString(), map);
    		}
    		return RECYCLER;
    	}else{
    		return RECYCLER;
    	}
    }
    
    public	Map<String, Map<String,Object>> loadAllCreations(BaseInputMessage inMessage){
    	if(CREATIONS.size() == 0){
    		List<Map<String,Object>> creations = stickerServiceImpl.selectAllCreations(inMessage);
    		for (Map<String, Object> map : creations) {
    			CREATIONS.put(map.get("creation_id").toString(), map);
    		}
    		return CREATIONS;
    	}else{
    		return CREATIONS;
    	}
    }
    
    
    
    public void loadData(){
    	logger.info("加载缓存map...");
    	BaseInputMessage inMessage = new BaseInputMessage();
    	loadAllManagerUser(inMessage);
    	loadAllUserAccount(inMessage);
    	loadAllDictGaeden(inMessage);
    	loadAllUserExtend(inMessage);
    	loadAllRecycler(inMessage);
    	loadAllCreations(inMessage);
    }
    
    protected boolean isNotLogin(BaseInputMessage inMessage){	
    	boolean flag = false;
    	Map<String, Object> manageruser = managerUserServiceImpl.queryManagerUser(inMessage);
		if(null == manageruser || manageruser.size() == 0){
			flag = true;
		}
		return flag;
    }
    
    protected boolean checkNull(BaseInputMessage inMessage){
    	String account = null== inMessage.getRequestMap().get("account")?"":inMessage.getRequestMap().get("account").toString();
    	String token = null== inMessage.getRequestMap().get("token")?"":inMessage.getRequestMap().get("token").toString();
    	boolean flag = false;
    	if (StringUtils.isEmpty(account) || StringUtils.isEmpty(token)) {
    		flag = true;
		}
    	return flag;
    }

    
    
    
    
 // 事件类型 返回对应的    有效值包括：1.厨余垃圾；2.小件投递；3.上门回收；4.活动奖励；255(0xFF).积分兑换。256.积分返还 
 	public static String genEventName(String eventtype) {
 		String eventname = "";
 		switch (eventtype) {
 		case "1":
 			eventname = "厨余垃圾";
 			break;
 		case "2":
 			eventname = "小件投递";
 			break;
 		case "3":
 			eventname = "上门回收";
 			break;
 		case "4":
 			eventname = "活动奖励";
 			break;
 		case "255":
 			eventname = "积分兑换";
 			break;
 		case "256":
 			eventname = "积分返还";
 			break;
 		}
 		return eventname;
 	}
 	
    /**
     * 
     * <p>
     * Description: 生成的JSON字符串放入response
     * </p>
     * 
     * @param response
     * @param json
     * @throws IOException
     * @author Jason.Guo
     * @date 2011-7-6
     */
    protected void writeJson(HttpServletResponse response, Object json,
            String status) {

        JSONObject jsonObject = JSONObject.fromObject(json);
        jsonObject.put("status", status);

        try {
            if (StringUtils.isNotEmpty((String) jsonObject.toString())) {
                response.setCharacterEncoding(Constants.DEFAULT_CHARSET);
                response.getWriter().write((String) jsonObject.toString());
            }
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    protected void writeJson(HttpServletResponse response, ModelAndView model)
            throws Exception {

        // 压缩返回
        try {
            model.addObject(JEEConstant.REQUEST_DATE,
                    DateUtils.getCurrentDateTimeSimpleFormat());
//            String reString = (String) JsonConvertor.object2Str(model
//                   .getModelMap());
            String reString = JSONObject.fromObject(model).toString();
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            GZIPOutputStream gout = new GZIPOutputStream(out);
            gout.write(reString.getBytes("UTF-8"));
            gout.finish();
            gout.flush();
            gout.close();

            response.setHeader("Content-Encoding", "gzip");
            response.setContentLength(out.toByteArray().length);
            response.setStatus(700);
            response.getOutputStream().write(out.toByteArray());
        } catch (Exception e) {
            throw new Exception(e.getMessage());
        }
    }
    protected void writeResponseStatus(ResponseStatus responseStatus,Map returnMap,HttpServletResponse response)throws Exception{
        returnMap.put("status"  ,responseStatus.getStatusCode());
        returnMap.put("message" ,responseStatus.getStatusName());
        writeJson(response, returnMap);
    }
    
    protected void writeJson(HttpServletResponse response, MsgHelper msgHelper)
            throws Exception {

        // 压缩返回
        try {
        	msgHelper.setRequest_date( DateUtils.getCurrentDateTimeSimpleFormat());
            String reString = JSONObject.fromObject(msgHelper).toString();
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            GZIPOutputStream gout = new GZIPOutputStream(out);
            gout.write(reString.getBytes("UTF-8"));
            gout.finish();
            gout.flush();
            gout.close();
            response.setContentType("text/html; charset=utf-8");
            response.setHeader("Content-Encoding", "gzip");
            response.setContentLength(out.toByteArray().length);
            response.setStatus(700);
            response.getOutputStream().write(out.toByteArray());
        } catch (Exception e) {
            throw new Exception(e.getMessage());
        }
    }
    
    
    
 // 正式环境不跨域返回
   /* protected void writeJson(HttpServletResponse response, Map<String, Object> returnMap)
    		throws Exception {
    	
    	// 压缩返回
    	try {
    		returnMap.put("timestamp", DateUtils.getCurrentDateTimeSimpleFormat());
    		String reString = JSONObject.fromObject(returnMap).toString();
    		ByteArrayOutputStream out = new ByteArrayOutputStream();
    		GZIPOutputStream gout = new GZIPOutputStream(out);
    		gout.write(reString.getBytes("UTF-8"));
    		gout.finish();
    		gout.flush();
    		gout.close();
    		response.setContentType("text/html; charset=utf-8");
    		response.setHeader("Content-Encoding", "gzip");
    		response.setContentLength(out.toByteArray().length);
    		response.setStatus(700);
    		response.getOutputStream().write(out.toByteArray());
    	} catch (Exception e) {
    		throw new Exception(e.getMessage());
    	}
    }*/
 // 测试是 跨域的 返回结果
 protected void ResponseStatus(ResponseStatus  ResponseStatus, Map<String, Object> returnMap)
         throws Exception {

 }
 	// 测试是 跨域的 返回结果
    protected void writeJson(HttpServletResponse response, Map<String, Object> returnMap)
    		throws Exception {
    	
    	// 压缩返回
    	try {
    		response.setHeader("Access-Control-Allow-Origin", "*"); // 解决跨域请求
 			response.setContentType("text/plain");
 			response.setHeader("Pragma", "No-cache");
 			response.setHeader("Cache-Control", "no-cache");
 			response.setDateHeader("Expires", 0);
    		returnMap.put("timestamp", DateUtils.getCurrentDateTimeSimpleFormat());
    		String reString = JSONObject.fromObject(returnMap).toString();
    		ByteArrayOutputStream out = new ByteArrayOutputStream();
    		GZIPOutputStream gout = new GZIPOutputStream(out);
    		gout.write(reString.getBytes("UTF-8"));
    		gout.finish();
    		gout.flush();
    		gout.close();
    		response.setContentType("text/html; charset=utf-8");
    		response.setHeader("Content-Encoding", "gzip");
    		response.setContentLength(out.toByteArray().length);
    		response.setStatus(201);
    		response.getOutputStream().write(out.toByteArray());
    	} catch (Exception e) {
    		throw new Exception(e.getMessage());
    	}
    }
    
    
    
    /**
     * 将异常封装到Message里面
     * <p>
     * Description:
     * </p>
     * 
     * @param e
     * @return
     * @author Jason.Guo
     * @date 2014-10-10
     */
    public BaseReturnMessage dealException(Exception e) {

        BaseReturnMessage message = new BaseReturnMessage();

        if (e instanceof JSONException) {
            createExceptionForMessage(message,
                    ExceptionCode.JSON_EXCEPTION_CODE,
                    ExceptionCode.JSON_EXCEPTION_REASON);
        } else if (e instanceof DBException) {
            createExceptionForMessage(message, ExceptionCode.DB_EXCEPTION_CODE,
                    ExceptionCode.DB_EXCEPTION_REASON);
        } else if (e instanceof NotLoginException) {
            createExceptionForMessage(message,
                    ExceptionCode.NOTLOGIN_EXCEPTION_CODE,
                    ExceptionCode.NOTLOGIN_EXCEPTION_REASON);
        } else if (e instanceof GenerateHtmlException) {
            createExceptionForMessage(message,
                    ExceptionCode.GENERATIONHHTML_EXCEPTION_CODE,
                    ExceptionCode.GENERATIONHHTML_EXCEPTION_REASON);
        } else if (e instanceof NotDataException) {
            createExceptionForMessage(message,
                    ExceptionCode.NOT_DATA_EXCEPTION_CODE, e.getMessage());
        } else if (e instanceof NotEnoughPrivilegeException) {
            createExceptionForMessage(message,
                    ExceptionCode.NOT_ENOUGH_PRIVILEGE_EXCEPTION_CODE,
                    ExceptionCode.NOT_ENOUGH_PRIVILEGE_EXCEPTION_REASON);
        } else if (e instanceof Exception) {
            createExceptionForMessage(message,
                    ExceptionCode.UNKOWN_EXCEPTION_CODE,
                    ExceptionCode.UNKOWN_EXCEPTION_REASON);
        }
        try {

            message.createErrorResult();
        } catch (Exception e1) {
            e1.printStackTrace();
        }
        return message;
    }

    private void createExceptionForMessage(BaseReturnMessage message,
            String code, String reason) {
        message.setCode(code);
        message.setDetail(reason);
    }

    
    
 // 解析请求的json格式数据
 	protected String genRequestParam(HttpServletRequest request) {
 		String requestParamJson = "{test:1}";
 		int i = 0;
 		for (String key : request.getParameterMap().keySet()) {
 			i++;
 			if (i == 1) {
 				requestParamJson = key;
 				break;
 			}
 		}
 		return requestParamJson;
 	}
 	
 	
 	/**
 	 * 将json请求的所有数据封装到map中
 	 * 
 	 * @param inMessage
 	 * @param reqObj
 	 */
 	protected void createConditionJsonToMap(BaseInputMessage inMessage, JSONObject reqObj) {
 		for (Iterator<String> keys = reqObj.keys(); keys.hasNext();) {
 			String key = keys.next();
 			inMessage.getRequestMap().put(key, reqObj.get(key));
 		}
		inMessage.getRequestMap().put(Constants.KEY_MAXRESULT, null==inMessage.getRequestMap().get(Constants.KEY_MAXRESULT)?Constants.DEFAYLT_KEY_MAXRESULT:(int) inMessage.getRequestMap().get(Constants.KEY_MAXRESULT));
		inMessage.getRequestMap().put(Constants.KEY_START, null==inMessage.getRequestMap().get(Constants.KEY_START)?Constants.DEFAULT_KEY_START:(int) inMessage.getRequestMap().get(Constants.KEY_START));

 	}
 	
 	
 	
 	// 过期时间失效
 	protected boolean checkTimestamp(long requestTime) {
 		boolean flag = false;
 		if (new Date().getTime() >= requestTime) {
 			flag = true;
 		}
 		return flag;
 	}
 	
    /**
     * 将request信息copy到message对象
     * <p>
     * Description:创建这次请求的基本参数
     * </p>
     * 
     * @param message
     * @author Jason.guo
     * @throws UnsupportedEncodingException
     * @date 2014-10-11
     */
    protected void createCondition(BaseInputMessage message,
            HttpServletRequest request) throws UnsupportedEncodingException {
        parameterMap = new HashMap();

        // 将request里面参数放入本类的属性parameterMap中
        convertRequestMap(request, message);
    }

    /**
     * 参数转换格式
     * <p>
     * Description:
     * </p>
     * 
     * @param request
     * @author Jason.guo
     * @throws UnsupportedEncodingException
     * @date 2014-10-11
     */

    public void convertRequestMap(HttpServletRequest request,
            BaseInputMessage message) throws UnsupportedEncodingException {
        Map parameterMap = message.getRequestMap();

        parameterMap.put(PRIMRYID, java.util.UUID.randomUUID().toString());
        if (null != request.getSession()
                && null != request.getSession().getAttribute(
                        SESSION_LOGIN_TOKEN)) {
        	Map<String,Object> user = (Map<String, Object>) request.getSession().getAttribute(
                    SESSION_LOGIN_TOKEN);
            if (null != user) {
                parameterMap.put(MANAGER_USER_ID, user.get("account_id"));
                parameterMap.put(MANAGER_USER_NAME, user.get("name"));
            }

        }

        if (request.getParameterMap() == null
                || request.getParameterMap().size() == 0) {
            setDefaultPaginationValue(parameterMap);
            return;
        } else {
            for (Object key : request.getParameterMap().keySet()) {
                if (Constants.KEY_START.equals(key.toString())
                        || Constants.KEY_MAXRESULT.equals(key.toString())) {
                    if (request.getParameter(key.toString()) == null
                            || "null".equals(request.getParameter(key
                                    .toString()))) {
                        parameterMap.put(key.toString(), -1);
                    } else {
                        try {
                            parameterMap.put(key.toString(), new Integer(
                                    request.getParameter(key.toString())));
                        } catch (Exception e) {
                            parameterMap.put(key.toString(), -1);
                        }
                    }

                } else {
                    Object obj = request.getParameter(key.toString());

                    if (StringUtils.equalsIgnoreCase(key.toString(),
                            "titleSearch")) {
                        if (obj instanceof String) {
                            String s = (String) obj;
                            s = new String(s.getBytes("ISO8859-1"), "UTF-8");
                            obj = s;
                        }
                    }

                    if (obj.toString().indexOf(Constants.COMMA_SPLITOR) != -1
                            && (key.toString().equals("id") || key.toString()
                                    .equals("items"))) {
                        parameterMap.put(
                                key.toString(),
                                Arrays.asList(obj.toString().split(
                                        Constants.COMMA_SPLITOR)));
                    } else {
                        parameterMap.put(
                                key.toString(),
                                obj != null ? obj.toString(): "");
                    }
                }

            }
        }

        // 如果start和mr为空,给它们默认值
        setDefaultPaginationValue(parameterMap);
    }

    /**
     * 
     * <p>
     * Description: list请求的时候翻页数值不能为空
     * </p>
     * 
     * @param parameterMap
     * @author Jason.Guo
     * @date 2013-4-6
     */
    public void setDefaultPaginationValue(Map parameterMap) {
        if (parameterMap.get(Constants.KEY_START) == null)
            parameterMap.put(Constants.KEY_START, 1);
        if (parameterMap.get(Constants.KEY_MAXRESULT) == null)
            parameterMap.put(Constants.KEY_MAXRESULT, Page.DEFAULT_PAGE_SIZE);
    }
    /**
     * 设置当前页到session
     * @param request
     * @param inMessage
     */
    public void setPageStart(HttpServletRequest request,BaseInputMessage inMessage){
    	 HttpSession session = request.getSession();
         session.setAttribute("start", inMessage.getRequestMap().get("start"));
    }
    /**
     * 从session取出当前页
     * @param request
     * @return
     */
    public String getPageStart(HttpServletRequest request){
   	 	HttpSession session = request.getSession();
        return session.getAttribute("start")!=null?"?start="+session.getAttribute("start").toString().toString():"";
   }

}
