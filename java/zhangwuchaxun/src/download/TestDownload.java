package download;

import java.util.HashMap;
import java.util.Map;


public class TestDownload {
	public void download(){
		String url = "http://bapi.jdpay.com/api/download.do";
		
		String filename = "";//具体格式请参考文档  例如：20151222ordercreate_110099385001.zip
		
		String path = "0001/";//具体格式请参考文档 例如：0001/0001 
		String key = "";//该参数由商户提供给网银在线进行配置 
		Map<String,String> req = new HashMap<String,String>();
		req.put("name", filename);
		req.put("path", path);
		String data = "{'name':'" + filename + "','path':'" + path + "'}";

		try {
			data = BASE64.encode(data.getBytes());//data进行BASE64
			String md5 = MD5.md5(data + key, "");
			Map<String,String> params = new HashMap<String,String>();
			params.put("md5", md5);
			params.put("data", data);
			params.put("owner", "");//owner为 商户在我方平台注册的9位商户号 例如：110099385
			WebUtils.download(url, params, 5000, 5000, "d:/download/"+filename);;
		} catch (Exception e) {
			e.printStackTrace();
		}



	}
	public static void main(String[] args) {
		new TestDownload().download();
	}
}
