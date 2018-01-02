package com.kyl.ps.interfaces.controller.impl;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.kyl.ps.constant.ResponseStatus;
import net.sf.json.JSONArray;
import net.sf.json.JSONObject;

import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import com.kyl.ps.infrastructure.service.impl.manageruser.ManagerUserServiceImpl;
import com.kyl.ps.interfaces.controller.AbstractController;
import com.kyl.ps.pojo.BaseInputMessage;
import com.kyl.ps.util.Constants;
import com.kyl.ps.util.MD5Util;

/**
 * 后台管理员
 * @author xiao.liao
 *
 */
@Controller
@RequestMapping("/authorization/*")
public class ManagerUserController extends AbstractController{

	Logger log = Logger.getLogger(ManagerUserController.class);
	@Autowired
	 ManagerUserServiceImpl managerUserServiceImpl;



	/**
	 * 管理员登陆
	 *
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/login", method = RequestMethod.POST)
	public void login(HttpServletRequest request,
			HttpServletResponse response) throws Exception {
		BaseInputMessage inMessage = new BaseInputMessage();
		Map<String, Object> returnMap = new HashMap<String, Object>();
		try {
//			this.createCondition(inMessage, request);
			String requestParam = this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
			String account = null == inMessage.getRequestMap().get("account")?"":inMessage.getRequestMap().get("account").toString();
			String password = null == inMessage.getRequestMap().get("password")?"":inMessage.getRequestMap().get("password").toString();
			log.info("login reqparams:" + inMessage.getRequestMap());
			if (StringUtils.isEmpty(account) || StringUtils.isEmpty(password)) {
				returnMap.put(Constants.STATUS, 405);
				returnMap.put(Constants.MESSAGE, "参数为空");
			} else {
				inMessage.getRequestMap().put("pwd", MD5Util.getMd5Str(password));
				Map<String, Object> manageruser = managerUserServiceImpl.queryManagerUser(inMessage);
				if(null == manageruser || manageruser.size() == 0){
					returnMap.put(Constants.STATUS, 2101);
					returnMap.put(Constants.MESSAGE, "登陆失败，账号或密码错误");
				}else{
					String token = null == manageruser.get("token")?"":manageruser.get("token").toString();
					String name = null == manageruser.get("name")?"":manageruser.get("name").toString();
					String account_id = null == manageruser.get("account_id")?"":manageruser.get("account_id").toString();
					if(StringUtils.isEmpty(token)){
						String uuid = UUID.randomUUID().toString();
					    token = MD5Util.getMd5Str((uuid+":"+System.currentTimeMillis()));
						// 更新token值
						inMessage.getRequestMap().put("token", token);
						managerUserServiceImpl.updateOmsAccount(inMessage);
					}
					returnMap.put("account", account);
					returnMap.put("token", token);
					returnMap.put("account_id", account_id);
					returnMap.put("name", name);
					returnMap.put("role_id" , 1);//测试
					returnMap.put(Constants.STATUS, Constants.STATUS_OK);
					returnMap.put(Constants.MESSAGE, "登陆成功");
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
			returnMap.put(Constants.STATUS, 500);
			returnMap.put(Constants.MESSAGE, "服务器异常");
		}
		// 返回数据
		log.info("【管理员登陆返回结果】:" + JSONObject.fromObject(returnMap));
		writeJson(response, returnMap);
	}


	/**
	 * 管理员登陆注销
	 *
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/loginout", method = RequestMethod.POST)
	public void loginout(HttpServletRequest request,
			HttpServletResponse response) throws Exception {
		BaseInputMessage inMessage = new BaseInputMessage();
		Map<String, Object> returnMap = new HashMap<String, Object>();
		try {
			String requestParam = this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
			String account = null == inMessage.getRequestMap().get("account")?"":inMessage.getRequestMap().get("account").toString();
			String token = null == inMessage.getRequestMap().get("token")?"":inMessage.getRequestMap().get("token").toString();
			log.info("loginout reqparams:" + inMessage.getRequestMap());
			if (StringUtils.isEmpty(account) || StringUtils.isEmpty(token)) {
				returnMap.put(Constants.STATUS, 405);
				returnMap.put(Constants.MESSAGE, "参数为空");
			} else {
				Map<String, Object> manageruser = managerUserServiceImpl.queryManagerUser(inMessage);
				if(null == manageruser || manageruser.size() == 0){
					returnMap.put(Constants.STATUS, 2201);
					returnMap.put(Constants.MESSAGE, "注销失败，验证不通过或已注销");
				}else{
					inMessage.getRequestMap().put("token", "");
					managerUserServiceImpl.updateOmsAccount(inMessage);
					returnMap.put(Constants.STATUS, Constants.STATUS_OK);
					returnMap.put(Constants.MESSAGE, "注销成功");
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
			returnMap.put(Constants.STATUS, 500);
			returnMap.put(Constants.MESSAGE, "服务器异常");
		}
		// 返回数据
		log.info("【管理员注销返回结果】:" + JSONObject.fromObject(returnMap));
		writeJson(response, returnMap);
	}
	/**
	 * 获取用户菜单列表
	 *
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/getUserRoleMenuList", method = RequestMethod.POST)
	public void getUserRoleMenu(HttpServletRequest request,
							HttpServletResponse response) throws Exception {
		BaseInputMessage 			inMessage 		= new BaseInputMessage();
		Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
		try {
			String 							requestParam 		= this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
			//获取角色菜单列表 通过角色列表进行判断 是否勾选
			List<Map<String, Object>>	 	queryUserRoleMenu	= managerUserServiceImpl.getUserRoleMenuList(inMessage);
			if(null == queryUserRoleMenu || queryUserRoleMenu.size() == 0){
				returnMap.put(Constants.STATUS, ResponseStatus.NOTPEPERMISSION.getStatusCode());
				returnMap.put(Constants.MESSAGE,  ResponseStatus.NOTPEPERMISSION.getStatusName());
			}
			returnMap.put("menuList",queryUserRoleMenu);
			returnMap.put(Constants.STATUS, Constants.STATUS_OK);
		} catch (Exception e) {
			e.printStackTrace();
			//returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
			//returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
		}
		// 返回数据
		log.info("【获取用户菜单列表】:" + JSONObject.fromObject(returnMap));
		writeJson(response, returnMap);
	}
	/**
	 * 设置角色权限
	 *
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/saveRoleMenu", method = RequestMethod.POST)
	public void saveRoleMenu(HttpServletRequest request,
								HttpServletResponse response) throws Exception {
		BaseInputMessage 			inMessage 		= new BaseInputMessage();
		Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
		try {
			String 							requestParam 		= this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
			//先删除角色之前权限
			managerUserServiceImpl.deleteRoleMenu(inMessage);
			String menuValues = inMessage.getRequestMap().get("moduleValues").toString();
			//生成数组
			inMessage.getRequestMap().put("moduleValues",menuValues.split(","));
			int	 	status	= managerUserServiceImpl.saveRoleMenu(inMessage);
			if(status == 0){
				throw new Exception("设置角色权限失败");
			}
			returnMap.put(Constants.STATUS, Constants.STATUS_OK);
		} catch (Exception e) {
			e.printStackTrace();
			//returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
			//returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
		}
		// 返回数据
		log.info("【设置角色权限】:" + JSONObject.fromObject(returnMap));
		writeJson(response, returnMap);
	}
	/**
	 * 获取角色菜单列表
	 *
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/getRoleMenuList", method = RequestMethod.POST)
	public void getRoleMenuList(HttpServletRequest request,
							HttpServletResponse response) throws Exception {
		BaseInputMessage 			inMessage 		= new BaseInputMessage();
		Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
		try {
			String 							requestParam 		= this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
			List<Map<String, Object>> 		queryAllMenu 		= managerUserServiceImpl.queryAllMenu();
			//获取角色菜单列表 通过角色列表进行判断 是否勾选
			List<Map<String, Object>>	 	queryUserRoleMenu	= managerUserServiceImpl.queryUserRoleMenu(inMessage);
			if(null == queryAllMenu || queryAllMenu.size() == 0){
				returnMap.put(Constants.STATUS, ResponseStatus.NOTPEPERMISSION.getStatusCode());
				returnMap.put(Constants.MESSAGE,  ResponseStatus.NOTPEPERMISSION.getStatusName());
			}
			JSONArray   returnMenu = new JSONArray();
			for(int i = 0 ; i<queryAllMenu.size();i++){
					JSONObject  returnJSON = new JSONObject();
				  	int  module_id = (int)queryAllMenu.get(i).get("module_id");
					returnJSON.put("module_name"	,queryAllMenu.get(i).get("name"));
					returnJSON.put("module_id"		,module_id);//是否被选中
					returnJSON.put("is_select"		,0);//是否被选中
				  	for(int j = 0 ; j<queryUserRoleMenu.size();j++){
					  int  module_idx = (int)queryUserRoleMenu.get(j).get("module_id");
					  if(module_idx == module_id){
						  returnJSON.put("is_select",1);//是否被选中
						  break;
					  }
				   }
					returnMenu.add(returnJSON);
			}
			returnMap.put("menuList",returnMenu.toString());
			returnMap.put(Constants.STATUS, Constants.STATUS_OK);

		} catch (Exception e) {
			e.printStackTrace();
			//returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
			//returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
		}
		// 返回数据
		log.info("【获取用户角色菜单返回接口】:" + JSONObject.fromObject(returnMap));
		writeJson(response, returnMap);
	}
	/**
	 * 获取角色列表
	 *
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/getRoleList", method = RequestMethod.POST)
	public void getRoleList(HttpServletRequest request,
								HttpServletResponse response) throws Exception {
		BaseInputMessage 			inMessage 		= new BaseInputMessage();
		Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
		try {
			//String 							requestParam 		= this.genRequestParam(request);
			List<Map<String, Object>>	 	queryUserRoleMenu	= managerUserServiceImpl.getRoleList();
			//returnMap.put("roleList"			,queryUserRoleMenu.toString());
			JSONArray   					returnMenu = new JSONArray();
			Map<String,Object>				tempList   = new HashMap<>();
			JSONArray						jsonArray  = new JSONArray();
			for(int i = 0 ; i<queryUserRoleMenu.size();i++){
				int   roleId  =  (int )queryUserRoleMenu.get(i).get("role_id");
				System.out.println("==tempList.containsKey(roleId)=="+tempList.containsValue(roleId)+"==roleId="+roleId);
				if(tempList.containsValue(queryUserRoleMenu.get(i).get("role_id"))){
					continue;
				}
				tempList.put("role_id",roleId);
				JSONObject    roleJson  = new JSONObject();
				roleJson.put("role_id"	,roleId);
				roleJson.put("role_name"	,queryUserRoleMenu.get(i).get("role_name"));
				JSONArray    userList   =  new JSONArray();
				for(int j = 0 ; j<queryUserRoleMenu.size();j++){
					    int userRoleId  =  (int )queryUserRoleMenu.get(j).get("role_id");
					    if(userRoleId == roleId){
							JSONObject   user = JSONObject.fromObject(queryUserRoleMenu.get(j));
							userList.add(user);
						}
				}
				roleJson.put("userList",userList);
				jsonArray.add(roleJson);
			}
			returnMap.put("roleList",jsonArray);
			returnMap.put(Constants.STATUS		, Constants.STATUS_OK);
		} catch (Exception e) {
			e.printStackTrace();
			returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
			returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
		}
		// 返回数据
		log.info("【获取角色列表】:" + JSONObject.fromObject(returnMap));
		writeJson(response, returnMap);
	}
	/***
	 * @description  获取用户列表 根据角色ID
	 * @param         request
	 * @param         response
	 * */
	@RequestMapping("getUserListByRoleId")
	public void getUserListByRoleId(HttpServletRequest request
			,HttpServletResponse response) throws  Exception{
		BaseInputMessage 			inMessage 		= new BaseInputMessage();
		Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
		ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
		try {
			String 							requestParam 		= this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
			List<Map<String, Object>>  list  = managerUserServiceImpl.getUserListByRoleId(inMessage);
			returnMap.put("userList",list);
			responseStatus      = ResponseStatus.SUCCESS;
		} catch (Exception e) {
			e.printStackTrace();
			returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
			returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
		}
		writeResponseStatus(responseStatus,returnMap,response);
		// 返回数据
		log.info("【根据角色获取用户列表接口】:" + JSONObject.fromObject(returnMap));
	}
	/***
	 * @description  获取用户角色列表 根据用户编号
	 * @param         request
	 * @param         response
	 * */
	@RequestMapping("getUserModuleByUserId")
	public void getUserModuleByUserId(HttpServletRequest request
			,HttpServletResponse response) throws  Exception{
		BaseInputMessage 			inMessage 		= new BaseInputMessage();
		Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
		ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
		try {
			String 							requestParam 		= this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
			List<Map<String, Object>> 		queryAllMenu 		= managerUserServiceImpl.queryAllMenu();
			//获取角色菜单列表 通过角色列表进行判断 是否勾选
			List<Map<String, Object>>	 	queryUserMenu	= managerUserServiceImpl.getUserModuleByUserId(inMessage);
			if(null == queryAllMenu || queryAllMenu.size() == 0){
				returnMap.put(Constants.STATUS, ResponseStatus.NOTPEPERMISSION.getStatusCode());
				returnMap.put(Constants.MESSAGE,  ResponseStatus.NOTPEPERMISSION.getStatusName());
			}
			JSONArray   returnMenu = new JSONArray();
			for(int i = 0 ; i<queryAllMenu.size();i++){
				JSONObject  returnJSON = new JSONObject();
				int  module_id = (int)queryAllMenu.get(i).get("module_id");
				returnJSON.put("module_name"	,queryAllMenu.get(i).get("name"));
				returnJSON.put("module_id"		,module_id);//是否被选中
				returnJSON.put("is_select"		,0);//是否被选中
				for(int j = 0 ; j<queryUserMenu.size();j++){
					int  module_idx = (int)queryUserMenu.get(j).get("module_id");
					if(module_idx == module_id){
						returnJSON.put("is_select",1);//是否被选中
						break;
					}
				}
				returnMenu.add(returnJSON);
			}
			//Map<String, Object>  map  = managerUserServiceImpl.queryManagerUserByUserId(inMessage);
			//returnMap.put("accountInfo"	,returnMenu);
			returnMap.put("menuList"		,returnMenu);
			responseStatus      = ResponseStatus.SUCCESS;
		} catch (Exception e) {
			e.printStackTrace();
			returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
			returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
		}
		writeResponseStatus(responseStatus,returnMap,response);
		// 返回数据
		log.info("【获取用户角色列表接口】:" + JSONObject.fromObject(returnMap));
	}
	/**
	 * 设置用户权限
	 *
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/saveUserModule", method = RequestMethod.POST)
	public void saveUserModule(HttpServletRequest request,
							 HttpServletResponse response) throws Exception {
		BaseInputMessage 			inMessage 		= new BaseInputMessage();
		Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
		ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
		try {
			String 							requestParam 		= this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
			//先删除用户之前权限
			managerUserServiceImpl.deleteUserModule(inMessage);
			String menuValues = inMessage.getRequestMap().get("moduleValues").toString();
			//生成数组
			inMessage.getRequestMap().put("moduleValues",menuValues.split(","));
			int	 	status	= managerUserServiceImpl.saveUserModule(inMessage);
			if(status == 0){
				throw new Exception("设置用户权限失败");
			}
			responseStatus      = ResponseStatus.SUCCESS;
		} catch (Exception e) {
			e.printStackTrace();
			returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
			returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
		}
		// 返回数据
		log.info("【设置用户权限接口】:" + JSONObject.fromObject(returnMap));
		writeResponseStatus(responseStatus,returnMap,response);
	}
	/**
	 * 新增角色
	 *
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/addRole", method = RequestMethod.POST)
	public void addRole(HttpServletRequest request,
							   HttpServletResponse response) throws Exception {
		BaseInputMessage 			inMessage 		= new BaseInputMessage();
		Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
		ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
		try {
			String 							requestParam 		= this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
			//先删除用户之前权限
			int  	status 				= managerUserServiceImpl.addRole(inMessage);
					returnMap.put("role_id",inMessage.getRequestMap().get("role_id"));
					responseStatus      = ResponseStatus.SUCCESS;
		} catch (Exception e) {
			e.printStackTrace();
			returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
			returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
		}
		// 返回数据
		log.info("【新增角色接口】:" + JSONObject.fromObject(returnMap));
		writeResponseStatus(responseStatus,returnMap,response);
	}
	/**
	 * 创建用户 根据用户名和密码就可以创建
	 *
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/createUser", method = RequestMethod.POST)
	public void createUser(HttpServletRequest request,
						HttpServletResponse response) throws Exception {
		BaseInputMessage 			inMessage 		= new BaseInputMessage();
		Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
		ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
		try {
			String 							requestParam 		= this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
			String  						password   			= inMessage.getRequestMap().get("password").toString().trim();
			inMessage.getRequestMap().put("pwd", MD5Util.getMd5Str(password));
			//需要判断用户名称是否已经存在
			int  							status 				= managerUserServiceImpl.createUser(inMessage);
			if(status > 0 ){
				if(null !=  inMessage.getRequestMap().get("moduleValues")){
					String 					menuValues 			= inMessage.getRequestMap().get("moduleValues").toString();
					//生成数组
					inMessage.getRequestMap().put("moduleValues",menuValues.split(","));
											status				= managerUserServiceImpl.saveUserModule(inMessage);
				}
			}
			returnMap.put("account_id",inMessage.getRequestMap().get("account_id"));
			responseStatus      = ResponseStatus.SUCCESS;
		} catch (Exception e) {
			e.printStackTrace();
		}
		// 返回数据
		log.info("【创建用户接口】:" + JSONObject.fromObject(returnMap));
		writeResponseStatus(responseStatus,returnMap,response);
	}
	/**
	 * 重置密码 根据用户名和密码就可以创建
	 *
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/resetPassword", method = RequestMethod.POST)
	public void resetPassword(HttpServletRequest request,
						   HttpServletResponse response) throws Exception {
		BaseInputMessage 			inMessage 		= new BaseInputMessage();
		Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
		ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
		try {
			String 							requestParam 		= this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
			String  						password   			= inMessage.getRequestMap().get("password").toString().trim();
			inMessage.getRequestMap().put("pwd", MD5Util.getMd5Str(password));
			int  	status 				= managerUserServiceImpl.resetPassword(inMessage);
			responseStatus      = ResponseStatus.SUCCESS;
		} catch (Exception e) {
			e.printStackTrace();
			returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
			returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
		}
		// 返回数据
		log.info("【重置密码接口】:" + JSONObject.fromObject(returnMap));
		writeResponseStatus(responseStatus,returnMap,response);
	}

	/**
	 * 获取所有用户基本信息
	 *
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/getAllUserInfoList", method = RequestMethod.POST)
	public void getAllUserInfoList(HttpServletRequest request,
							  HttpServletResponse response) throws Exception {
		BaseInputMessage 			inMessage 		= new BaseInputMessage();
		Map<String, Object> 		returnMap 		= new HashMap<String, Object>();
		ResponseStatus              responseStatus  = ResponseStatus.SERVERERROR;
		try {
			String 							requestParam 		= this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage, JSONObject.fromObject(requestParam));
			//返回最新数据给客户端
			Map<String,Object>          pageTotalMap    = managerUserServiceImpl.getAllUserInfoListCount(inMessage);
			int                         pageTotal       = ((Long)pageTotalMap.get("pageTotal")).intValue();
			//获取名称是否已经存在 如果存在 则直接提示

			int                         start           = (int)inMessage.getRequestMap().get(Constants.KEY_START);
			int                         mr              = (int)inMessage.getRequestMap().get(Constants.KEY_MAXRESULT);
			inMessage.getRequestMap().put(Constants.KEY_START,Math.abs(start-1)*mr);
			List<Map<String,Object>>		list	= managerUserServiceImpl.getAllUserInfoList(inMessage);
			returnMap.put("userInfoList",list);
			int totalPageSize = pageTotal % mr;
			if(totalPageSize == 0 ) returnMap.put("pageTotal",pageTotal/mr);
			else returnMap.put("pageTotal",(pageTotal/mr)+1);
			responseStatus      = ResponseStatus.SUCCESS;
		} catch (Exception e) {
			e.printStackTrace();
			returnMap.put(Constants.STATUS, ResponseStatus.SERVERERROR.getStatusCode());
			returnMap.put(Constants.MESSAGE,  ResponseStatus.SERVERERROR.getStatusName());
		}
		// 返回数据
		log.info("【获取所有用户基本信息】:" + JSONObject.fromObject(returnMap));
		writeResponseStatus(responseStatus,returnMap,response);
	}

}
