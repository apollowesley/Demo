package com.kyl.ps.interfaces.controller.impl;

import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import net.sf.json.JSONObject;

import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import com.kyl.ps.infrastructure.service.impl.customer.CustomerServiceImpl;
import com.kyl.ps.infrastructure.service.impl.recycler.RecyclerServiceImpl;
import com.kyl.ps.interfaces.controller.AbstractController;
import com.kyl.ps.pojo.BaseInputMessage;
import com.kyl.ps.util.Constants;
import com.kyl.ps.util.DateUtils;

/**
 * 回收人员管理
 * 
 * @author xiao.liao
 *
 */
@Controller
@RequestMapping("/recycler/*")
public class RecyclerController extends AbstractController {
	private static final Logger log = Logger.getLogger(RecyclerController.class);

	@Autowired
	private RecyclerServiceImpl recyclerServiceImpl;
	@Autowired
	private CustomerServiceImpl customerServiceImpl;

	/**
	 * 编辑保存回收人员信息
	 * 
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@RequestMapping(value = "/editrecycler", method = RequestMethod.POST)
	public void editrecycler(HttpServletRequest request,
			HttpServletResponse response) throws Exception {
		BaseInputMessage inMessage = new BaseInputMessage();
		Map<String, Object> returnMap = new HashMap<String, Object>();
		long start = System.currentTimeMillis();
		try {
			String requestParam = this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage,
					JSONObject.fromObject(requestParam));
			log.info("----recycler editrecycler reqparams:"
					+ requestParam);
			String recycler_id = null == inMessage.getRequestMap().get(
					"recycler_id") ? "" : inMessage.getRequestMap()
					.get("recycler_id").toString();
			String state = null == inMessage.getRequestMap().get("state") ? ""
					: inMessage.getRequestMap().get("state").toString();
			if (checkNull(inMessage) || StringUtils.isEmpty(recycler_id) || StringUtils.isEmpty(state)) {
				returnMap.put(Constants.STATUS, 405);
				returnMap.put(Constants.MESSAGE, "参数为空");
				throw new Exception();
			}
			if (isNotLogin(inMessage)) {
				returnMap.put(Constants.STATUS, 4301);
				returnMap.put(Constants.MESSAGE, "未登陆或权限验证失败");
				throw new Exception();
			}
			
			recyclerServiceImpl.editRecycler(inMessage);
			if(null != RECYCLER && RECYCLER.size() > 0){
				RECYCLER.clear();
				loadData();
			}
			returnMap.put(Constants.STATUS, Constants.STATUS_OK);
			returnMap.put(Constants.MESSAGE, "调用成功");
		} catch (Exception e) {
			if (returnMap.size() == 0) {
				e.printStackTrace();
				returnMap.put(Constants.STATUS, 500);
				returnMap.put(Constants.MESSAGE, "服务器异常");
			}
		}
		log.info("【编辑保存回收人员信息】" + JSONObject.fromObject(returnMap) + ", 耗时：" +(System.currentTimeMillis() - start));
		writeJson(response, returnMap);
	}

	
	
	
	/**
	 * 查詢回收人员列表
	 * 
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/recyclers", method = RequestMethod.POST)
	public void recyclers(HttpServletRequest request,
			HttpServletResponse response) throws Exception {
		BaseInputMessage inMessage = new BaseInputMessage();
		Map<String, Object> returnMap = new HashMap<String, Object>();
		long starttime = System.currentTimeMillis();
		try {
			String requestParam = this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage,
					JSONObject.fromObject(requestParam));
			log.info("----recycler recyclers reqparams:"
					+ requestParam);
			if (checkNull(inMessage)) {
				returnMap.put(Constants.STATUS, 405);
				returnMap.put(Constants.MESSAGE, "参数为空");
				throw new Exception();
			}
			if (isNotLogin(inMessage)) {
				returnMap.put(Constants.STATUS, 4101);
				returnMap.put(Constants.MESSAGE, "未登陆或权限验证失败");
				throw new Exception();
			}

			// 根据状态查询     0：在职，1：离职，2：待审。  不传：查询全部（默认）
			String state = null == inMessage.getRequestMap().get(
					"state") ? "" : inMessage.getRequestMap()
					.get("state").toString();
			String queryname = null == inMessage.getRequestMap().get(
					"queryname") ? "" : inMessage.getRequestMap()
							.get("queryname").toString();
			int mr = (int) inMessage.getRequestMap().get("mr");
			int start = (int) inMessage.getRequestMap().get("start");

			inMessage.getRequestMap().put("state", state);
			inMessage.getRequestMap().put("startnum", (start - 1) * mr);
			inMessage.getRequestMap().put("mr", mr);

			if(StringUtils.isNotEmpty(queryname)){
				inMessage.getRequestMap().put("phone", queryname);
			}
			
			int total = recyclerServiceImpl.queryRecyclesCount(inMessage);
			List<Map<String, Object>> recyclers = recyclerServiceImpl.queryRecycles(inMessage);
			
			
			for (Map<String, Object> map : recyclers) {
				map.put("update_time",
						null == map.get("update_time") ? ""
								: DateUtils.date2StrInSecond((Date) map
										.get("update_time")));
				map.put("creation_time",
						null == map.get("creation_time") ? "" : DateUtils
								.date2StrInSecond((Date) map
										.get("creation_time")));
				
				// 根据回收人员id查询，是否登陆状态
				String recycler_id = null == map.get("recycler_id") ? "" : map
						.get("recycler_id").toString();
				 inMessage.getRequestMap().put("user_id", recycler_id);
				 Map<String,Object> usermobile = customerServiceImpl.queryUserMobileById(inMessage);
				 if(null != usermobile && usermobile.size()>0){
					 String token = null == usermobile.get("token") ? "" : usermobile
								.get("token").toString();
					 if(StringUtils.isNotEmpty(token)){
						 String url = request.getRequestURL().toString();
						 url = url.substring(0, url.lastIndexOf("/"));
						 String downloadUrl = url + "/logoff?recycler_id="+ recycler_id;
						 map.put("logoff_url", downloadUrl); // 已登录的 可注销
					 }
				 }
				 
				 
			}

			returnMap.put("total", total);
			returnMap.put(Constants.RESULT_ITEMS, recyclers);
			returnMap.put(Constants.STATUS, Constants.STATUS_OK);
			returnMap.put(Constants.MESSAGE, "调用成功");

		} catch (Exception e) {
			if (returnMap.size() == 0) {
				e.printStackTrace();
				returnMap.put(Constants.STATUS, 500);
				returnMap.put(Constants.MESSAGE, "服务器异常");
			}
		}
		log.debug("result:" + JSONObject.fromObject(returnMap));
		log.info("【查詢回收人员列表】, 耗时：" +(System.currentTimeMillis() - starttime) + "ms, " + returnMap.get(Constants.MESSAGE));
		writeJson(response, returnMap);
	}

	
	
	
	/**
	 * 回收人员注销登陆状态
	 * 
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/logoff", method = RequestMethod.GET)
	public void logoff(HttpServletRequest request,
			HttpServletResponse response) throws Exception {
		BaseInputMessage inMessage = new BaseInputMessage();
		Map<String, Object> returnMap = new HashMap<String, Object>();
		long starttime = System.currentTimeMillis();
		try {
			this.convertRequestMap(request, inMessage);
			String recycler_id = null == inMessage.getRequestMap().get(
					"recycler_id") ? "" : inMessage.getRequestMap()
					.get("recycler_id").toString();
			log.info("----recycler logoff recycler_id="
					+ recycler_id);

			if(StringUtils.isEmpty(recycler_id)){
				returnMap.put(Constants.STATUS, 405);
				returnMap.put(Constants.MESSAGE, "参数为空");
				throw new Exception();
			}
			
			inMessage.getRequestMap().put("user_id", recycler_id);
			// 注销回收人员的登陆状态
			customerServiceImpl.updateUserMobileById(inMessage);
			returnMap.put(Constants.STATUS, Constants.STATUS_OK);
			returnMap.put(Constants.MESSAGE, "调用成功");

		} catch (Exception e) {
			if (returnMap.size() == 0) {
				e.printStackTrace();
				returnMap.put(Constants.STATUS, 500);
				returnMap.put(Constants.MESSAGE, "服务器异常");
			}
		}
		log.debug("result:" + JSONObject.fromObject(returnMap));
		log.info("【回收人员注销登陆状态】, 耗时：" +(System.currentTimeMillis() - starttime) + "ms, " + returnMap.get(Constants.MESSAGE));
		writeJson(response, returnMap);
	}
}
