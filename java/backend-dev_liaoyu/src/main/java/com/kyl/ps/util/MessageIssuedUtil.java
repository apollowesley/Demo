package com.kyl.ps.util;

import java.io.UnsupportedEncodingException;
import java.net.MalformedURLException;
import java.util.HashMap;
import java.util.Map;

import net.sf.json.JSONObject;

import com.taobao.api.ApiException;
import com.taobao.api.DefaultTaobaoClient;
import com.taobao.api.TaobaoClient;
import com.taobao.api.request.AlibabaAliqinFcSmsNumSendRequest;
import com.taobao.api.response.AlibabaAliqinFcSmsNumSendResponse;


/**
 * 下发验证码
 * @author xiao.liao
 *
 */
public class MessageIssuedUtil {

	
	public static void main(String[] args) throws MalformedURLException, UnsupportedEncodingException {
		String code = RandNumGenerator.generateRandNum();
		int result = aLiDaYe("18701016199",code);
		if (result == 0) {
			System.out.println("发送成功");
		}else{
			System.out.println("发送失败");
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
	public static int aLiDaYe(String sendPhone, String code) throws MalformedURLException, UnsupportedEncodingException {
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
		req.setExtend("123456");
		req.setSmsType("normal");
		req.setSmsFreeSignName("买么");// 短信签名
		req.setSmsParamString(jsonObject.toString());
		req.setRecNum(sendPhone);// 接收手机号
		// 模板Id
		req.setSmsTemplateCode(templateCode); // 短信模板id
		AlibabaAliqinFcSmsNumSendResponse rsp;
		try {
			rsp = client.execute(req);
			String str = rsp.getBody();
			System.out.println(str);
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
