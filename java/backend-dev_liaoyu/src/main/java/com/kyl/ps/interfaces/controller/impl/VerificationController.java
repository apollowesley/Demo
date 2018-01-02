package com.kyl.ps.interfaces.controller.impl;

import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.net.MalformedURLException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import net.sf.json.JSONObject;

import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ClassPathXmlApplicationContext;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import com.kyl.ps.infrastructure.service.impl.manageruser.VerificationServiceImpl;
import com.kyl.ps.interfaces.controller.AbstractController;
import com.kyl.ps.pojo.BaseInputMessage;
import com.kyl.ps.pojo.MsgHelper;
import com.kyl.ps.util.DESHelper;
import com.kyl.ps.util.PropertiesUtil;
import com.kyl.ps.util.RandNumGenerator;
import com.taobao.api.ApiException;
import com.taobao.api.DefaultTaobaoClient;
import com.taobao.api.TaobaoClient;
import com.taobao.api.request.AlibabaAliqinFcSmsNumSendRequest;
import com.taobao.api.response.AlibabaAliqinFcSmsNumSendResponse;
/**
 * 验证码下发， 校验
 * @author xiao.liao
 *
 */
@Controller
@RequestMapping("/verification/*")
public class VerificationController extends AbstractController {
	private static final Logger log = Logger.getLogger(VerificationController.class);


	@Autowired
	private VerificationServiceImpl verificationServiceImpl;

	
	@SuppressWarnings("unchecked")
	public static void main(String[] args) throws Exception {
		ApplicationContext context = new ClassPathXmlApplicationContext("applicationContext.xml");
		VerificationServiceImpl verificationServiceImpl = (VerificationServiceImpl) context.getBean("verificationServiceImpl");
		BaseInputMessage inMessage = new BaseInputMessage();
		inMessage.getRequestMap().put("code", "111222");
		inMessage.getRequestMap().put("phone", DESHelper.getInstance().encrypt("18701016199"));
		inMessage.getRequestMap().put("status", 0);
		verificationServiceImpl.insertCode(inMessage);
		
	}
	
	/**
	 * 下发验证码
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/generate", method = RequestMethod.POST)
	public synchronized void generate(HttpServletRequest request, HttpServletResponse response) throws Exception {
		BaseInputMessage inMessage = new BaseInputMessage();
		MsgHelper msgHelper = new MsgHelper();
		try {
			this.createCondition(inMessage, request);
			DESHelper des = DESHelper.getInstance();
			String phone = request.getParameter("phone");
			inMessage.getRequestMap().put("phone", des.encrypt(phone));// 加密
			if (phone == null || phone.equals("")) {
				msgHelper.setMessage("参数为空");
				msgHelper.setStatus(MsgHelper.ERROR_DATA_CODE);
			} else {
				SimpleDateFormat formatter1 = new SimpleDateFormat("yyyy-MM-dd");
				String date = formatter1.format(new Date());
				inMessage.getRequestMap().put("startTime", date + " 00:00:00");
				inMessage.getRequestMap().put("endTime", date + " 23:59:59");
				int tiao = verificationServiceImpl.CodeShuMu(inMessage);
				if (tiao >= 5) { // 同用户每日限制次数
					msgHelper.setMessage("超出可发次数");
					msgHelper.setStatus(MsgHelper.ERROR_DATA_CODE);
				} else {
					String code = RandNumGenerator.generateRandNum();
					inMessage.getRequestMap().put("code", code);
					int result = 0;
					try {
						result = this.aLiDaYe(phone, code);
					} catch (Exception e) {
						result = -2;
					}
					if (result == 0) {
						msgHelper.setMessage("发送成功");
						msgHelper.setResult(code);
						msgHelper.setStatus(MsgHelper.SUCCESS_CODE);
					} else {
						msgHelper.setMessage("发送失败");
						msgHelper.setStatus(MsgHelper.ERROR_DATA_CODE);
					}
					inMessage.getRequestMap().put("status", result);
					verificationServiceImpl.insertCode(inMessage);

				}
			}
		} catch (Exception e) {
			e.printStackTrace();
			msgHelper.setMessage("异常");
			msgHelper.setStatus(MsgHelper.ERROR_DATA_CODE);
		}
		// 跨域请求

		String jsonpCallback = request.getParameter("callback");// 客户端请求参数
		if (null != jsonpCallback && !"".equals(jsonpCallback)) {
//			String reffer = request.getHeader("Referer");
			response.setHeader("Access-Control-Allow-Origin", "*"); // 解决跨域请求
			response.setContentType("text/plain");
			response.setHeader("Pragma", "No-cache");
			response.setHeader("Cache-Control", "no-cache");
			response.setDateHeader("Expires", 0);
			PrintWriter out = response.getWriter();
			JSONObject resultJSON = JSONObject.fromObject(msgHelper); // 根据需要拼装json
			out.println(jsonpCallback + "(" + resultJSON.toString(1, 1) + ")");// 返回jsonp格式数据
			out.flush();
			out.close();

		} else {
			// 返回数据
			writeJson(response, msgHelper);
		}
	}

	
	/**
	 * 验证手机号，绑定二维码便签
	 * @param request
	 * @param response
	 * @throws Exception
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/verifys", method = RequestMethod.POST)
	public synchronized void verifys(HttpServletRequest request, HttpServletResponse response) throws Exception {
		MsgHelper msgHelper = new MsgHelper();
		BaseInputMessage inMessage = new BaseInputMessage();
		try {
			this.createCondition(inMessage, request);
			DESHelper des = DESHelper.getInstance();
			String phone = request.getParameter("phone");
			String code = request.getParameter("code");
			inMessage.getRequestMap().put("phone", des.encrypt(phone));
				if (null == phone || phone.equals("") || null == code || code.equals("")) {
					log.info("参数不能为空");
					msgHelper.setMessage("参数为空");
					msgHelper.setStatus(MsgHelper.ERROR_DATA_CODE);
				} else {
					int cuanZai = verificationServiceImpl.selectCode(inMessage);
					if (cuanZai > 0) {
						// TODO  保存该用户扫描的二维码信息
						msgHelper.setMessage("验证成功");
						msgHelper.setStatus(MsgHelper.SUCCESS_CODE);
					} else {
						log.info("验证码错误");
						msgHelper.setMessage("验证码错误");
						msgHelper.setStatus(MsgHelper.ERROR_DATA_CODE);
					}
				}
		} catch (Exception e) {
			e.printStackTrace();
			msgHelper.setMessage("异常");
			msgHelper.setStatus(MsgHelper.ERROR_DATA_CODE);
		}
		// 跨域请求

		String jsonpCallback = request.getParameter("callback");// 客户端请求参数
		if (null != jsonpCallback && !"".equals(jsonpCallback)) {
			response.setHeader("Access-Control-Allow-Origin", "*"); // 解决跨域请求
			response.setContentType("text/plain");
			response.setHeader("Pragma", "No-cache");
			response.setHeader("Cache-Control", "no-cache");
			response.setDateHeader("Expires", 0);
			PrintWriter out = response.getWriter();
			JSONObject resultJSON = JSONObject.fromObject(msgHelper); // 根据需要拼装json
			out.println(jsonpCallback + "(" + resultJSON.toString(1, 1) + ")");// 返回jsonp格式数据
			out.flush();
			out.close();

		} else {
			// 返回数据
			writeJson(response, msgHelper);
		}
	}

	/**
	 * 阿里大鱼短信发送接口
	 * 
	 * @param sendPhone
	 * @param code
	 * @return int
	 * @throws MalformedURLException
	 * @throws UnsupportedEncodingException
	 */
	private int aLiDaYe(String sendPhone, String code) throws MalformedURLException, UnsupportedEncodingException {
		int inputaLiDaYe = -1;
		String code1 = PropertiesUtil.getValue("common", "server.code").trim();
		Map<String, Object> map = new HashMap<String, Object>();
		map.put("code0", code);
		map.put("code1", code1);
		JSONObject jsonObject = JSONObject.fromObject(map);
		String url = "http://gw.api.taobao.com/router/rest";
		String appkey = PropertiesUtil.getValue("common", "server.appkey").trim();// 23446753
		String secret = PropertiesUtil.getValue("common", "server.secret").trim();// 465e879a5c4c05b01f2fc72981c6be27
		String templateCode = PropertiesUtil.getValue("common", "server.temp.late.code").trim();//SMS_14246381
		TaobaoClient client = new DefaultTaobaoClient(url, appkey, secret);
		AlibabaAliqinFcSmsNumSendRequest req = new AlibabaAliqinFcSmsNumSendRequest();
		// 短信类型，传入值请填写normal
		req.setSmsType("normal");
		req.setSmsFreeSignName("买么");
		req.setSmsParamString(jsonObject.toString());
		req.setRecNum(sendPhone);
		// 模板Id
		req.setSmsTemplateCode(templateCode);
		AlibabaAliqinFcSmsNumSendResponse rsp;
		try {
			rsp = client.execute(req);
			String str = rsp.getBody();
			if (str != null) {
				JSONObject object = JSONObject.fromObject(str);
				String stest = (null != object.get("alibaba_aliqin_fc_sms_num_send_response")
						? object.get("alibaba_aliqin_fc_sms_num_send_response").toString() : "");
				if (!stest.equals("")) {
					inputaLiDaYe = 0;
				} else {
					inputaLiDaYe = -1;
				}
			} else {
				inputaLiDaYe = -1;
			}
		} catch (ApiException e) {
			inputaLiDaYe = -1;
		}
		return inputaLiDaYe;
	}
}
