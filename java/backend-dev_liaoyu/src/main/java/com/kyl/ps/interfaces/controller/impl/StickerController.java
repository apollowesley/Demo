package com.kyl.ps.interfaces.controller.impl;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.util.ArrayList;
import java.util.Collections;
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

import com.kyl.ps.infrastructure.service.impl.collect.CollectServiceImpl;
import com.kyl.ps.infrastructure.service.impl.customer.CustomerServiceImpl;
import com.kyl.ps.infrastructure.service.impl.manageruser.ManagerUserServiceImpl;
import com.kyl.ps.infrastructure.service.impl.recycler.RecyclerServiceImpl;
import com.kyl.ps.infrastructure.service.impl.sticker.StickerServiceImpl;
import com.kyl.ps.interfaces.controller.AbstractController;
import com.kyl.ps.model.manageruser.ManagerUser;
import com.kyl.ps.pojo.BaseInputMessage;
import com.kyl.ps.pojo.MyComparator;
import com.kyl.ps.util.Constants;
import com.kyl.ps.util.DateUtils;
import com.kyl.ps.util.HelpDownloadUtil;

/**
 * 二维码贴纸管理
 * 
 * @author xiao.liao
 *
 */
@Controller
@RequestMapping("/sticker/*")
public class StickerController extends AbstractController {
	private static final Logger log = Logger.getLogger(StickerController.class);

	@Autowired
	private StickerServiceImpl stickerServiceImpl;
	@Autowired
	private ManagerUserServiceImpl managerUserServiceImpl;
	@Autowired
	private CustomerServiceImpl customerServiceImpl;
	@Autowired
	private RecyclerServiceImpl recyclerServiceImpl;
	@Autowired
	private CollectServiceImpl collectServiceImpl;

	/**
	 * 批次号名称查询
	 * 
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/existcreationname", method = RequestMethod.POST)
	public void existcreationname(HttpServletRequest request,
			HttpServletResponse response) throws Exception {
		BaseInputMessage inMessage = new BaseInputMessage();
		Map<String, Object> returnMap = new HashMap<String, Object>();
		try {
			String requestParam = this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage,
					JSONObject.fromObject(requestParam));
			log.info("----stickers existcreationname reqparams:"
					+ requestParam);
			String creationname = null == inMessage.getRequestMap().get(
					"creationname") ? "" : inMessage.getRequestMap()
					.get("creationname").toString();

			if (StringUtils.isEmpty(creationname)) {
				log.info(inMessage.getRequestMap());
				returnMap.put(Constants.STATUS, 405);
				returnMap.put(Constants.MESSAGE, "参数为空");
				throw new Exception();
			}

			inMessage.getRequestMap().put("startnum", 0);
			inMessage.getRequestMap().put("mr", 1);
			inMessage.getRequestMap().put("name", creationname);
			List<Map<String, Object>> creations = stickerServiceImpl
					.selectCreations(inMessage);
			if (null == creations || creations.size() == 0) {
				returnMap.put("state", 0);// 批次号名称状态 0：正常可用， 1：已存在
			} else {
				returnMap.put("state", 1);
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
		writeJson(response, returnMap);
	}

	/**
	 * 新增贴纸批次记录
	 * 
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/newcreations", method = RequestMethod.POST)
	public void newcreations(HttpServletRequest request,
			HttpServletResponse response) throws Exception {
		BaseInputMessage inMessage = new BaseInputMessage();
		Map<String, Object> returnMap = new HashMap<String, Object>();
		long start = System.currentTimeMillis();
		try {
			String requestParam = this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage,
					JSONObject.fromObject(requestParam));
			log.info("----stickers newcreations reqparams:"
					+ requestParam);
			String account_id = null == inMessage.getRequestMap().get(
					"account_id") ? "" : inMessage.getRequestMap()
					.get("account_id").toString();
			String prefix = null == inMessage.getRequestMap().get("prefix") ? ""
					: inMessage.getRequestMap().get("prefix").toString();
			String account = null == inMessage.getRequestMap().get("account") ? ""
					: inMessage.getRequestMap().get("account").toString();
			String token = null == inMessage.getRequestMap().get("token") ? ""
					: inMessage.getRequestMap().get("token").toString();
			String rolls = null == inMessage.getRequestMap().get("rolls") ? "0"
					: inMessage.getRequestMap().get("rolls").toString();
			int areaCode = null == inMessage.getRequestMap().get("areaCode") ? 0
					: Integer.parseInt(inMessage.getRequestMap().get("areaCode").toString());
			
			
			String rolls_quantity = null == inMessage.getRequestMap().get(
					"rolls_quantity") ? "" : inMessage.getRequestMap()
					.get("rolls_quantity").toString();
			String expiration_time = null == inMessage.getRequestMap().get(
					"expiration_time") ? "" : inMessage.getRequestMap()
					.get("expiration_time").toString();
			String name = null == inMessage.getRequestMap().get("name") ? ""
					: inMessage.getRequestMap().get("name").toString();// 印刷批次记录名称。

			if (StringUtils.isEmpty(account_id) || StringUtils.isEmpty(prefix)
					|| StringUtils.isEmpty(account)
					|| StringUtils.isEmpty(token) || StringUtils.isEmpty(rolls)
					|| StringUtils.isEmpty(rolls_quantity)
					|| StringUtils.isEmpty(expiration_time)
					|| StringUtils.isEmpty(name) || areaCode ==0) {
				log.info(inMessage.getRequestMap());
				returnMap.put(Constants.STATUS, 405);
				returnMap.put(Constants.MESSAGE, "参数为空");
				throw new Exception();
			}
			if (isNotLogin(inMessage)) {
				returnMap.put(Constants.STATUS, 3301);
				returnMap.put(Constants.MESSAGE, "未登陆或权限验证失败");
				throw new Exception();
			}

			// 过期时间 已失效
			if (checkTimestamp(DateUtils.str2DateInSecond(expiration_time)
					.getTime())) {
				returnMap.put(Constants.STATUS, 3302);
				returnMap.put(Constants.MESSAGE, "失效时间已过期");
				throw new Exception();
			}
			if (Integer.parseInt(rolls) > Constants.MAX_ROLLS) {
				returnMap.put(Constants.STATUS, 3303);
				returnMap.put(Constants.MESSAGE, "卷数超出限制");
				throw new Exception();
			}

			inMessage.getRequestMap().put("prefix_code", areaCode);
			int count  = stickerServiceImpl.selectAreaPrefixCode(inMessage);
			if (count == 0) {
				returnMap.put(Constants.STATUS, 3304);
				returnMap.put(Constants.MESSAGE, "该区域前缀编号不存在");
				throw new Exception();
			}
			
			inMessage.getRequestMap().put("startnum", 0);
			inMessage.getRequestMap().put("mr", 1);
			inMessage.getRequestMap().put("name", name);
			List<Map<String, Object>> creations = stickerServiceImpl
					.selectCreations(inMessage);
			if (null == creations || creations.size() == 0) {
				ManagerUser managerUser = new ManagerUser();
				managerUser.setAccountId(Integer.parseInt(account_id));
				managerUser.setPrefix(prefix);
				managerUser.setRolls(Integer.parseInt(rolls));
				managerUser.setRollsQuantity(Integer.parseInt(rolls_quantity));
				managerUser.setExpirationTime(expiration_time);
				managerUser.setName(name);
				stickerServiceImpl.insertCreationsRetKey(managerUser, areaCode);
				returnMap.put(Constants.STATUS, Constants.STATUS_OK);
				returnMap.put(Constants.MESSAGE, "调用成功");
				
				if(null != CREATIONS && CREATIONS.size() > 0){
					CREATIONS.clear();
					loadData();
				}
			} else {
				returnMap.put(Constants.STATUS, 3304);
				returnMap.put(Constants.MESSAGE, "该批次号名称已存在");
			}

		} catch (Exception e) {
			if (returnMap.size() == 0) {
				e.printStackTrace();
				returnMap.put(Constants.STATUS, 500);
				returnMap.put(Constants.MESSAGE, "服务器异常");
			}
		}
		log.info("【新建贴纸印刷批次】" + JSONObject.fromObject(returnMap) + ", 耗时：" +(System.currentTimeMillis() - start));
		writeJson(response, returnMap);
	}

	/**
	 * 查詢贴纸生成批次记录
	 * 
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/creations", method = RequestMethod.POST)
	public void creations(HttpServletRequest request,
			HttpServletResponse response) throws Exception {
		BaseInputMessage inMessage = new BaseInputMessage();
		Map<String, Object> returnMap = new HashMap<String, Object>();
		long starttime = System.currentTimeMillis();
		try {
			// this.createCondition(inMessage, request);
			String requestParam = this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage,
					JSONObject.fromObject(requestParam));
			log.info("----stickers creations reqparams:"
					+ requestParam);
			if (checkNull(inMessage)) {
				returnMap.put(Constants.STATUS, 405);
				returnMap.put(Constants.MESSAGE, "参数为空");
				throw new Exception();
			}
			if (isNotLogin(inMessage)) {
				returnMap.put(Constants.STATUS, 3101);
				returnMap.put(Constants.MESSAGE, "未登陆或权限验证失败");
				throw new Exception();
			}

			// 根据状态查询 0：使用中 ，1：已激活 为空：查询全部
			String recordstatus = null == inMessage.getRequestMap().get(
					"recordstatus") ? "" : inMessage.getRequestMap()
					.get("recordstatus").toString();
			int mr = (int) inMessage.getRequestMap().get("mr");
			int start = (int) inMessage.getRequestMap().get("start");
			loadData();

			inMessage.getRequestMap().put("record_status", recordstatus);
			inMessage.getRequestMap().put("startnum", (start - 1) * mr);
			inMessage.getRequestMap().put("mr", mr);

			int total = stickerServiceImpl.selectCreationsCount(inMessage);
			List<Map<String, Object>> creations = stickerServiceImpl
					.selectCreations(inMessage);
			
			for (Map<String, Object> map : creations) {
				int record_status = null == map.get("record_status") ? 0
						: (int)map.get("record_status");
				String creator_id = null == map.get("creator_id") ? "" : map
						.get("creator_id").toString();
				String creation_name = null == map.get("name") ? "" : map
						.get("name").toString();
				String creation_id = null == map.get("creation_id") ? "" : map
						.get("creation_id").toString();
				map.put("manager_name",
						null == MANAGER_USER.get(creator_id) ? ""
								: MANAGER_USER.get(creator_id).get("name"));
				map.put("update_time",
						null == map.get("update_time") ? ""
								: DateUtils.date2StrInSecond((Date) map
										.get("update_time")));
				map.put("expiration_time",
						null == map.get("expiration_time") ? "" : DateUtils
								.date2StrInSecond((Date) map
										.get("expiration_time")));
				map.put("creation_time",
						null == map.get("creation_time") ? "" : DateUtils
								.date2StrInSecond((Date) map
										.get("creation_time")));
				map.put("record_status", record_status);
				if ( 0 == record_status) {//未激活，可下载
					String url = request.getRequestURL().toString();
					url = url.substring(0, url.lastIndexOf("/"));
					String downloadUrl = url + "/downloads?creation_id="+ creation_id;
					map.put("downloads_url", downloadUrl); // 未激活时，提供该条数据的下载链接
					map.put("name_url", url+"/downloads?creation_name="+creation_name); // 未激活时，提供该批次的下载链接
				}
			}

			returnMap.put(Constants.RESULT_TOTAL, total);
			returnMap.put(Constants.RESULT_ITEMS, creations);
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
		log.info("【查询贴纸印刷批次】, 耗时：" +(System.currentTimeMillis() - starttime) + "ms, " + returnMap.get(Constants.MESSAGE));
		writeJson(response, returnMap);
	}

	/**
	 * 查詢所有贴纸列表信息
	 * 
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/stickers", method = RequestMethod.POST)
	public void stickers(HttpServletRequest request,
			HttpServletResponse response) throws Exception {
		BaseInputMessage inMessage = new BaseInputMessage();
		Map<String, Object> returnMap = new HashMap<String, Object>();
		long stime = System.currentTimeMillis();
		try {
			// this.createCondition(inMessage, request);
			String requestParam = this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage,
					JSONObject.fromObject(requestParam));
			log.info("----stickers stickers reqparams:"
					+ requestParam);
			if (checkNull(inMessage)) {
				returnMap.put(Constants.STATUS, 405);
				returnMap.put(Constants.MESSAGE, "参数为空");
				throw new Exception();
			}
			if (isNotLogin(inMessage)) {
				returnMap.put(Constants.STATUS, 3201);
				returnMap.put(Constants.MESSAGE, "未登陆或权限验证失败");
				throw new Exception();
			}
			int mr = (int) inMessage.getRequestMap().get("mr");
			int start = (int) inMessage.getRequestMap().get("start");

			loadData();
			inMessage.getRequestMap().put("startnum", (start - 1) * mr);
			inMessage.getRequestMap().put("mr", mr);

			// 根据字段模糊查询 type: 1：贴纸编号模糊查询(默认) 2：印刷批次编号模糊查询
			String type = null == inMessage.getRequestMap().get("type") ? ""
					: inMessage.getRequestMap().get("type").toString();
			String status = null == inMessage.getRequestMap().get("status") ? ""
					: inMessage.getRequestMap().get("status").toString(); //贴纸状态：  0.未激活；1.已激活
			// 模糊查询的内容,为空查询所有
			String queryname = null == inMessage.getRequestMap().get(
					"queryname") ? "" : inMessage.getRequestMap()
					.get("queryname").toString();
			if (StringUtils.isNotEmpty(queryname)) {
				if ("1".equals(type)) {
					inMessage.getRequestMap().put("sticker_id", queryname);
				} else if ("2".equals(type)) {
					inMessage.getRequestMap().put("creation_name", queryname);// 印刷批次名称模糊查询
				}
			}	
			
			if (StringUtils.isNotEmpty(status)) {
				inMessage.getRequestMap().put("status", status);
			}	

			int total = stickerServiceImpl.selectStickersCount(inMessage);
			List<Map<String, Object>> stickers = stickerServiceImpl
					.selectStickers(inMessage);
			for (Map<String, Object> map : stickers) {
				String creator_id = null == map.get("creator_id") ? "" : map
						.get("creator_id").toString();// 创建贴纸批次管理员id
				String creation_id = null == map.get("creation_id") ? "" : map
						.get("creation_id").toString();// 批次编号
				map.put("manager_name",
						null == MANAGER_USER.get(creator_id) ? ""
								: MANAGER_USER.get(creator_id).get("name"));
				map.put("name",
						null == CREATIONS.get(creation_id) ? ""
								: CREATIONS.get(creation_id).get("name"));// 印刷批次名称

				// 显示关联用户的手机号
				String user_id = null == map.get("user_id") ? "" : map.get(
						"user_id").toString();// 关联用户的id
				map.put("phone", null == USER_ACCOUNT.get(user_id) ? ""
						: USER_ACCOUNT.get(user_id).get("phone"));
				map.put("active_time",
						null == map.get("active_time") ? ""
								: DateUtils.date2StrInSecond((Date) map
										.get("active_time")));
				map.put("expiration_time",
						null == map.get("expiration_time") ? "" : DateUtils
								.date2StrInSecond((Date) map
										.get("expiration_time")));
				map.put("creation_time",
						null == map.get("creation_time") ? "" : DateUtils
								.date2StrInSecond((Date) map
										.get("creation_time")));
			}

			returnMap.put(Constants.RESULT_TOTAL, total);
			returnMap.put(Constants.RESULT_ITEMS, stickers);
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
		log.info("【查询贴纸信息列表】, 耗时：" +(System.currentTimeMillis() - stime)  + "ms, " + returnMap.get(Constants.MESSAGE));
		writeJson(response, returnMap);
	}

	/**
	 * @Description：下载贴纸批次信息
	 */
	/*@SuppressWarnings({ "deprecation", "unchecked" })
	@RequestMapping(value = "/downloads", method = RequestMethod.GET)
	public void downloads(HttpServletRequest request,
			HttpServletResponse response) throws Exception {
		BaseInputMessage inMessage = new BaseInputMessage();
		String fileName = "贴纸印刷批次信息" + UUID.randomUUID().toString();
		Map<String, Object> returnMap = new HashMap<String, Object>();
		try {
			this.convertRequestMap(request, inMessage);
			log.info("----stickers downloads reqparams:"
					+ inMessage.getRequestMap());
			String creation_id = null == inMessage.getRequestMap().get(
					"creation_id") ? "" : inMessage.getRequestMap()
					.get("creation_id").toString();
			
			String creation_name = null == inMessage.getRequestMap().get(
					"creation_name") ? "" : inMessage.getRequestMap()
							.get("creation_name").toString();

			if (StringUtils.isEmpty(creation_id) && StringUtils.isEmpty(creation_name)) {// 至少一个必须有值
				returnMap.put(Constants.STATUS, 405);
				returnMap.put(Constants.MESSAGE, "参数为空");
				writeJson(response, returnMap);
			} else {
				inMessage.getRequestMap().put("startnum", 0);
				inMessage.getRequestMap().put("mr", 1);
				inMessage.getRequestMap().put("creation_id", creation_id);
				inMessage.getRequestMap().put("record_status", 0);// 0 :正常 ，
																	// 1：已激活
				List<Map<String, Object>> creations = stickerServiceImpl
						.selectCreations(inMessage);
				if (null == creations || creations.size() == 0) {
					returnMap.put(Constants.STATUS, 3301);
					returnMap.put(Constants.MESSAGE, "贴纸批次编号不存在或已被激活");
					writeJson(response, returnMap);
				} else {
					loadData();
					Map<String, Object> creation = creations.get(0);
					int downloads = null == creation.get("downloads") ? 0
							: (int) creation.get("downloads");
					log.info(" --- creation_id=" + creation_id + ", 之前的下载次数为："
							+ downloads);

					String creator_id = null == creation.get("creator_id") ? ""
							: creation.get("creator_id").toString();
					String manager_name = null == MANAGER_USER.get(creator_id) ? ""
							: MANAGER_USER.get(creator_id).get("name")
									.toString();

					final String fileType = ".xls";
					String download = request.getRealPath("/download");
					String filePath = download + "/" + fileName + fileType;
					boolean flag = ExcelUtil.CreateExcel(download, fileName,
							fileType, creations.get(0), manager_name);
					if (flag) {
						HelpDownloadUtil.download(response,
								fileName + fileType, filePath);

						// 更新下载次数
						inMessage.getRequestMap().put("downloads",
								downloads + 1);
						stickerServiceImpl.updateCreation(inMessage);
					} else {
						returnMap.put(Constants.STATUS, 3402);
						returnMap.put(Constants.MESSAGE, "下载失败");
						writeJson(response, returnMap);
					}
					new File(filePath).delete();
				}
			}

		} catch (Exception e) {
			if (returnMap.size() == 0) {
				e.printStackTrace();
				returnMap.put(Constants.STATUS, 500);
				returnMap.put(Constants.MESSAGE, "服务器异常");
			}
		}

	}*/
	/**
	 * @Description：下载贴纸批次信息，  一条 或多条
	 */
	@SuppressWarnings({ "unchecked" })
	@RequestMapping(value = "/downloads", method = RequestMethod.GET)
	public void downloads(HttpServletRequest request,
			HttpServletResponse response) throws Exception {
		BaseInputMessage inMessage = new BaseInputMessage();
		String fileName = "";
		Map<String, Object> returnMap = new HashMap<String, Object>();
//		BufferedWriter write = null;
		Writer write = null;
		try {
			this.convertRequestMap(request, inMessage);
			log.info("----stickers downloads reqparams:"
					+ inMessage.getRequestMap());
			String creation_id = null == inMessage.getRequestMap().get(
					"creation_id") ? "" : inMessage.getRequestMap()
							.get("creation_id").toString();
			
			String creation_name = null == inMessage.getRequestMap().get(
					"creation_name") ? "" : inMessage.getRequestMap()
							.get("creation_name").toString();
			
			if (StringUtils.isEmpty(creation_id) && StringUtils.isEmpty(creation_name)) {// 至少一个必须有值
				returnMap.put(Constants.STATUS, 405);
				returnMap.put(Constants.MESSAGE, "参数为空");
				writeJson(response, returnMap);
			} else {
				inMessage.getRequestMap().put("startnum", 0);
				inMessage.getRequestMap().put("mr", 1);
				inMessage.getRequestMap().put("record_status", 0);// 0 :正常(未激活的才可下载) ，1：已激活  
				loadData();
				if(StringUtils.isNotEmpty(creation_id)){
					fileName = null == CREATIONS.get(creation_id) ? "印刷批次下载"
							: CREATIONS.get(creation_id).get("name").toString();
					// 根据批次编号下载一条贴纸数据
					write = downloadById(request, response, inMessage,
							fileName, returnMap, write, creation_id);
				}else if(StringUtils.isNotEmpty(creation_name)){
					// 根据 批次名称下载 对应的所有贴纸数据
					fileName = creation_name;
					write = downloadByName(request, response, inMessage,
							fileName, returnMap, write, creation_id,
							creation_name);
				}
			}
			
		} catch (Exception e) {
			if (returnMap.size() == 0) {
				e.printStackTrace();
				returnMap.put(Constants.STATUS, 500);
				returnMap.put(Constants.MESSAGE, "服务器异常");
			}
		}finally{
			try {
				if(null != write){
					write.close();
				}
			} catch (Exception e2) {
			}
		}
		
	}
public static void main(String[] args) {
	System.out.println("\r\n");
	System.out.println("12");
}
	
	// 根据批次印刷名称， 下载该批次的所有贴纸数据
	@SuppressWarnings({ "unchecked", "deprecation" })
	private Writer downloadByName(HttpServletRequest request,
			HttpServletResponse response, BaseInputMessage inMessage,
			String fileName, Map<String, Object> returnMap,
			Writer write, String creation_id, String creation_name)
			throws Exception, IOException {
		// 根据批次名称查询对于的所有批次编号
		inMessage.getRequestMap().put("name", creation_name);
		List<Map<String, Object>> creations = stickerServiceImpl
				.selectCreations(inMessage);
		if (null == creations || creations.size() == 0) {
			returnMap.put(Constants.STATUS, 3301);
			returnMap.put(Constants.MESSAGE, "贴纸批次编号不存在或已被激活");
			writeJson(response, returnMap);
		} else {
			Map<String, Object> creation = creations.get(0);
			int downloads = null == creation.get("downloads") ? 0
					: (int) creation.get("downloads");
			log.info(" --- creation_name=" + creation_name + ", 之前的下载次数为："
					+ downloads);
			
			String prefix = null == creation.get("prefix") ? "" : creation.get("prefix").toString();
			String rolls_quantity = null == creation.get("rolls_quantity") ? "" : creation.get("rolls_quantity").toString();
			
			final String fileType = ".txt";
			String download = request.getRealPath("/download");
			String filePath = download + "/" + fileName + fileType;
			 File file = new File(download);
			    if(!file.exists()){
			    	file.mkdir();
			    }
			List<Map<String, Object>> stickers = stickerServiceImpl.selectStickersBycreationName(inMessage);
			if(null != stickers && stickers.size()>0){
				write = new OutputStreamWriter(new FileOutputStream(filePath),"Unicode");
				write.write("编号,二维码,数量\r\n");
				write.flush();
				for (Map<String, Object> sticker : stickers) {
					String rolltag = null == sticker.get("roll_tag") ? "" : sticker.get("roll_tag").toString();
					String sticker_id = null == sticker.get("sticker_id") ? "" : sticker.get("sticker_id").toString();
					String qrcodeurl = "";
					if(prefix.lastIndexOf("?")!=-1){
						qrcodeurl = prefix + sticker_id;
					}else{
						qrcodeurl = prefix + "?id=" + sticker_id;
					}
					
					write.write(rolltag + "," + qrcodeurl + "," + rolls_quantity + "\r\n");
					write.flush();
				}
				
				HelpDownloadUtil.download(response,
						fileName + fileType, filePath);
				
				// 更新该批次名称对应的所有下载次数
				stickerServiceImpl.updateCreationByName(inMessage);
			}
			
			new File(filePath).delete();
		}
		return write;
	}
	
	

	// 根据批次编号下载一条数据
	@SuppressWarnings({ "unchecked", "deprecation" })
	private Writer downloadById(HttpServletRequest request,
			HttpServletResponse response, BaseInputMessage inMessage,
			String fileName, Map<String, Object> returnMap,
			Writer write, String creation_id) throws Exception,
			IOException {
		inMessage.getRequestMap().put("creation_id", creation_id);
		List<Map<String, Object>> creations = stickerServiceImpl
				.selectCreations(inMessage);
		if (null == creations || creations.size() == 0) {
			returnMap.put(Constants.STATUS, 3301);
			returnMap.put(Constants.MESSAGE, "贴纸批次编号不存在或已被激活");
			writeJson(response, returnMap);
		} else {
			Map<String, Object> creation = creations.get(0);
			int downloads = null == creation.get("downloads") ? 0
					: (int) creation.get("downloads");
			log.info(" --- creation_id=" + creation_id + ", 之前的下载次数为："
					+ downloads);
			
			String prefix = null == creation.get("prefix") ? "" : creation.get("prefix").toString();
			String rolls_quantity = null == creation.get("rolls_quantity") ? "" : creation.get("rolls_quantity").toString();
			
			final String fileType = ".txt";
			String download = request.getRealPath("/download");
			String filePath = download + "/" + fileName + fileType;
			 File file = new File(download);
			    if(!file.exists()){
			    	file.mkdir();
			    }
			    
			// 根据批次编号 查询t_sticker贴纸对应的罗马标记和贴纸编号
			List<Map<String, Object>> stickers = stickerServiceImpl
						.selectStickers(inMessage);   
			if(null != stickers && stickers.size()>0){
				Map<String, Object> sticker = stickers.get(0);
				String rolltag = null == sticker.get("roll_tag") ? "" : sticker.get("roll_tag").toString();
				String sticker_id = null == sticker.get("sticker_id") ? "" : sticker.get("sticker_id").toString();
				String qrcodeurl = "";
				if(prefix.lastIndexOf("?")!=-1){
					qrcodeurl = prefix + sticker_id;
				}else{
					qrcodeurl = prefix + "?id=" + sticker_id;
				}
				
				write = new OutputStreamWriter(new FileOutputStream(filePath),"Unicode");
				write.write("编号,二维码,数量\r\n");
				write.flush();
				write.write(rolltag + "," + qrcodeurl+"," + rolls_quantity +"\r\n");
				write.flush();
				
				HelpDownloadUtil.download(response,
						fileName + fileType, filePath);
				
				// 更新下载次数
				inMessage.getRequestMap().put("downloads",
						downloads + 1);
				stickerServiceImpl.updateCreation(inMessage);
			}
			    
			new File(filePath).delete();
		}
		return write;
	}

	/**
	 * 查詢某一贴纸记录的详情（批次信息， 关联用户信息， 使用记录信息）
	 * 
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@RequestMapping(value = "/detail", method = RequestMethod.POST)
	public void detail(HttpServletRequest request, HttpServletResponse response)
			throws Exception {
		BaseInputMessage inMessage = new BaseInputMessage();
		Map<String, Object> returnMap = new HashMap<String, Object>();
		List<Map<String, Object>> jsonMaplist = new ArrayList<Map<String, Object>>();
		long s = System.currentTimeMillis();
		try {
			String requestParam = this.genRequestParam(request);
			this.createConditionJsonToMap(inMessage,
					JSONObject.fromObject(requestParam));
			String creation_id = null == inMessage.getRequestMap().get(
					"creation_id") ? "" : inMessage.getRequestMap()
					.get("creation_id").toString();
			String sticker_id = null == inMessage.getRequestMap().get(
					"sticker_id") ? "" : inMessage.getRequestMap()
							.get("sticker_id").toString();
			String user_id = null == inMessage.getRequestMap().get("user_id") ? ""
					: inMessage.getRequestMap().get("user_id").toString();
			String type = null == inMessage.getRequestMap().get("type") ? "1"
					: inMessage.getRequestMap().get("type").toString();
			log.info("----stickers detail:" + requestParam);
			if (checkNull(inMessage) || StringUtils.isEmpty(creation_id)
					|| StringUtils.isEmpty(type) || StringUtils.isEmpty(sticker_id)) {
				returnMap.put(Constants.STATUS, 405);
				returnMap.put(Constants.MESSAGE, "参数为空");
				throw new Exception();
			}

			if (isNotLogin(inMessage)) {
				returnMap.put(Constants.STATUS, 3501);
				returnMap.put(Constants.MESSAGE, "未登陆或权限验证失败");
				throw new Exception();
			}

			loadData();
			
			// 查询印刷批次
			if ("1".equals(type)) {
				queryCreationDetail(inMessage, returnMap, jsonMaplist,
						creation_id);
			} else {
				if (StringUtils.isNotEmpty(user_id)) {
					// 查看关联用户
					if ("2".equals(type)) {
						queryUserDetail(inMessage, returnMap, jsonMaplist,
								user_id);
					}
					// 查看贴纸使用记录
					else if ("3".equals(type)) {
						queryStickerUsedlDetail(inMessage, returnMap, sticker_id);
					}
				} else {
					// 该贴纸未激活，无关联用户和使用记录
					returnMap.put(Constants.RESULT_ITEMS, "");
					returnMap.put(Constants.STATUS, Constants.STATUS_OK);
					returnMap.put(Constants.MESSAGE, "调用成功");
				}
			}

			returnMap.put("type", Integer.parseInt(type));
			
		} catch (Exception e) {
			if (returnMap.size() == 0) {
				e.printStackTrace();
				returnMap.put(Constants.STATUS, 500);
				returnMap.put(Constants.MESSAGE, "服务器异常");
			}
		}
		log.debug("result:" + JSONObject.fromObject(returnMap));
		log.info("【查询贴纸详情信息】, 耗时：" +(System.currentTimeMillis() - s)  + "ms, " + returnMap.get(Constants.MESSAGE));
		writeJson(response, returnMap);
	}
	
	
	
	
	// 查询该用户的所有贴纸使用记录
	@SuppressWarnings({ "unchecked", "unused" })
	private void queryUserIntegerDetail(BaseInputMessage inMessage,
			Map<String, Object> returnMap, String sticker_id) {
		int mr = (int) inMessage.getRequestMap().get("mr");
		int start = (int) inMessage.getRequestMap().get("start");
		inMessage.getRequestMap().put("startnum", (start - 1) * mr);
		inMessage.getRequestMap().put("mr", mr);
		 // 该用户的所有贴纸使用记录
		  int total = customerServiceImpl.queryUsagerecordCount(inMessage);
		List<Map<String, Object>> usagerecords = customerServiceImpl
				.queryUsagerecord(inMessage);
		for (Map<String, Object> map : usagerecords) {
			String recycler_id = null == map.get("recycler_id") ? "" : map.get("recycler_id").toString();// 回收人员编号
			map.put("name",null == RECYCLER.get(recycler_id) ? "": RECYCLER.get(recycler_id).get("name"));// 回收人员名称
			String userid = null == map.get("user_id") ? "" : map.get("user_id").toString();// 用户编号
			map.put("address",null == USER_EXTEND.get(userid) ? "": USER_EXTEND.get(userid).get("address"));// 用户使用地址
			
			String event_type = null == map.get("event_type") ? "" : map.get("event_type").toString();
			map.put("eventname",genEventName(event_type));// 事件名称
			map.put("event_time",
					null == map.get("event_time") ? "" : DateUtils
							.date2StrInSecond((Date) map
									.get("event_time")));
		}
		returnMap.put(Constants.RESULT_TOTAL, total);
		returnMap.put(Constants.RESULT_ITEMS, usagerecords);
		returnMap.put(Constants.STATUS, Constants.STATUS_OK);
		returnMap.put(Constants.MESSAGE, "调用成功");
	}
	
	
	
	
	
	
	

	// 查询该贴纸的所有使用记录
	@SuppressWarnings("unchecked")
	private void queryStickerUsedlDetail(BaseInputMessage inMessage,
			Map<String, Object> returnMap, String sticker_id) throws Exception {
		int mr = (int) inMessage.getRequestMap().get("mr");
		int start = (int) inMessage.getRequestMap().get("start");
		inMessage.getRequestMap().put("sticker_id", sticker_id);
		List<Map<String, Object>> stickerRecords = new ArrayList<Map<String,Object>>();
		
		int kitchenTotal = collectServiceImpl.queryKitchenBySidCount(inMessage);
		int garbageTotal = collectServiceImpl.queryGarbageBySidCount(inMessage);
		int total = kitchenTotal + garbageTotal;
		
		// 该贴纸的所有厨余记录
		List<Map<String, Object>> kitchens = collectServiceImpl.queryKitchenBySid(inMessage);
		combinationRetDatas(kitchens, "厨余垃圾");
		
		// 该贴纸的所有小件投递记录
		List<Map<String, Object>> garbages = collectServiceImpl.queryGarbageBySid(inMessage);
		combinationRetDatas(garbages, "小件投递");
		
		stickerRecords.addAll(kitchens);
		stickerRecords.addAll(garbages);
		Collections.sort(stickerRecords, new MyComparator());
		
		int totalpage = 0 == total%mr ? total/mr : total/mr + 1; 
		if(start <= totalpage){
			if(total >= start * mr){
				stickerRecords = stickerRecords.subList((start - 1) * mr, mr*start);
			}else{
				stickerRecords = stickerRecords.subList((start - 1) * mr, stickerRecords.size());
			}
		}else{
			stickerRecords = new ArrayList<Map<String,Object>>();
		}
		
		returnMap.put("mr", mr);
		returnMap.put("start", start);
		returnMap.put(Constants.RESULT_TOTAL, total);
		returnMap.put(Constants.RESULT_ITEMS, stickerRecords);
		returnMap.put(Constants.STATUS, Constants.STATUS_OK);
		returnMap.put(Constants.MESSAGE, "调用成功");
	}

	
	
	private void combinationRetDatas(List<Map<String, Object>> kitchens,
			String eventname) {
		for (Map<String, Object> map : kitchens) {
			String recycler_id = null == map.get("recycler_id") ? "" : map.get("recycler_id").toString();// 回收人员编号
			map.put("name",null == RECYCLER.get(recycler_id) ? "": RECYCLER.get(recycler_id).get("name"));// 回收人员名称
			String userid = null == map.get("user_id") ? "" : map.get("user_id").toString();// 用户编号
			map.put("address",null == USER_EXTEND.get(userid) ? "": USER_EXTEND.get(userid).get("address"));// 用户使用地址
			map.put("eventname",eventname);// 事件名称
			map.put("collect_time",
					null == map.get("collect_time") ? "" : DateUtils
							.date2StrInSecond((Date) map
									.get("collect_time")));
		}
	}

	
	// 查看几乎该帖子的用户信息
	@SuppressWarnings("unchecked")
	private void queryUserDetail(BaseInputMessage inMessage,
			Map<String, Object> returnMap,
			List<Map<String, Object>> jsonMaplist, String user_id) {
		inMessage.getRequestMap().put("startnum", 0);
		inMessage.getRequestMap().put("mr", 1);
		Map<String, Object> customer = customerServiceImpl
				.queryCustomerInfo(inMessage);

		if (null != customer && customer.size() > 0) {
			String garden_id = null == customer.get("garden_id") ? "" : customer.get("garden_id").toString();// 小区id
			customer.put("address",null == USER_EXTEND.get(user_id) ? "": USER_EXTEND.get(user_id).get("address"));// 用户详细地址
			customer.put("name",null == DICT_GARDEN.get(garden_id) ? "": DICT_GARDEN.get(garden_id).get("name"));// 小区名称
			customer.put("username",null == USER_ACCOUNT.get(user_id) ? "": USER_ACCOUNT.get(user_id).get("name"));// 用户名称
			customer.put("update_time",
					null == customer.get("update_time") ? ""
							: DateUtils.date2StrInSecond((Date) customer
									.get("update_time")));
			customer.put("creation_time",
					null == customer.get("creation_time") ? "" : DateUtils
							.date2StrInSecond((Date) customer
									.get("creation_time")));
		}

		jsonMaplist.add(customer);
		returnMap.put(Constants.RESULT_TOTAL, jsonMaplist.size());
		returnMap.put(Constants.RESULT_ITEMS, jsonMaplist);
		returnMap.put(Constants.STATUS, Constants.STATUS_OK);
		returnMap.put(Constants.MESSAGE, "调用成功");
	}

	// 查询贴纸批次信息
	@SuppressWarnings("unchecked")
	private void queryCreationDetail(BaseInputMessage inMessage,
			Map<String, Object> returnMap,
			List<Map<String, Object>> jsonMaplist, String creation_id) {
		inMessage.getRequestMap().put("startnum", 0);
		inMessage.getRequestMap().put("mr", 1);
		inMessage.getRequestMap().put("creation_id", creation_id);
		List<Map<String, Object>> creations  = stickerServiceImpl.selectCreations(inMessage);
		Map<String, Object> map = new HashMap<String, Object>();
		if(null != creations && creations.size() > 0){
			map = creations.get(0);
			map.put("expiration_time",
					null == map.get("expiration_time") ? "" : DateUtils
							.date2StrInSecond((Date) map
									.get("expiration_time")));
			map.put("creation_time",
					null == map.get("creation_time") ? "" : DateUtils
							.date2StrInSecond((Date) map
									.get("creation_time")));
			map.put("update_time",
					null == map.get("update_time") ? "" : DateUtils
							.date2StrInSecond((Date) map
									.get("update_time")));
		}
		jsonMaplist.add(map);
		returnMap.put(Constants.RESULT_TOTAL, jsonMaplist.size());
		returnMap.put(Constants.RESULT_ITEMS, jsonMaplist);
		returnMap.put(Constants.STATUS, Constants.STATUS_OK);
		returnMap.put(Constants.MESSAGE, "调用成功");
	}
}
