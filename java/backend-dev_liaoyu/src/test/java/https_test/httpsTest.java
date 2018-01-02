package https_test;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.ConnectException;
import java.net.URL;
import java.net.URLConnection;

import javax.net.ssl.SSLSocketFactory;

import net.sf.json.JSONObject;

import com.sun.net.ssl.HttpsURLConnection;
import com.sun.net.ssl.SSLContext;
import com.sun.net.ssl.TrustManager;


public class httpsTest {

	public static void main(String[] args) throws Exception {
		// TODO Auto-generated method stub

//		JSONObject json = httpRequest("https://www.sun.com","post","test");
//		System.out.println(json);
		
		System.out.println("222:" + requsetUrl("https://www.sun.com"));
		
//		URL reqURL = new URL("https://www.sun.com" ); //创建URL对象
//		HttpsURLConnection httpsConn = (HttpsURLConnection)reqURL.openConnection();
//
//		//取得该连接的输入流，以读取响应内容
//		InputStreamReader insr = new InputStreamReader(httpsConn.getInputStream());
//
//		//读取服务器的响应内容并显示
//		int respInt = insr.read();
//		while( respInt != -1){
//		System.out.print((char)respInt);
//		respInt = insr.read();
//		}
	}

	
	
	public static JSONObject httpRequest(String requestUrl, String requestMethod, String outputStr) {    
	       JSONObject jsonObject = null;    
	       StringBuffer buffer = new StringBuffer();    
	       try {    
	           // 创建SSLContext对象，并使用我们指定的信任管理器初始化    
	           TrustManager[] tm = { (TrustManager) new MyX509TrustManager() };    
	           SSLContext sslContext = SSLContext.getInstance("SSL", "SunJSSE");    
	           sslContext.init(null, tm, new java.security.SecureRandom());    
	           // 从上述SSLContext对象中得到SSLSocketFactory对象    
	           SSLSocketFactory ssf = sslContext.getSocketFactory();    
	   
	           URL url = new URL(requestUrl);    
	           HttpsURLConnection httpUrlConn = (HttpsURLConnection) url.openConnection();    
	           httpUrlConn.setSSLSocketFactory(ssf);    
	   
	           httpUrlConn.setDoOutput(true);    
	           httpUrlConn.setDoInput(true);    
	           httpUrlConn.setUseCaches(false);    
	           // 设置请求方式（GET/POST）    
	           httpUrlConn.setRequestMethod(requestMethod);    
	   
	           if ("GET".equalsIgnoreCase(requestMethod))  {  
	              
	            httpUrlConn.connect();    
	           }  
	   
	           // 当有数据需要提交时    
	           if (null != outputStr) {    
	               OutputStream outputStream = httpUrlConn.getOutputStream();    
	               // 注意编码格式，防止中文乱码    
	               outputStream.write(outputStr.getBytes("UTF-8"));    
	               outputStream.close();    
	           }    
	   
	           // 将返回的输入流转换成字符串    
	           InputStream inputStream = httpUrlConn.getInputStream();    
	           InputStreamReader inputStreamReader = new InputStreamReader(inputStream, "utf-8");    
	           BufferedReader bufferedReader = new BufferedReader(inputStreamReader);    
	   
	           String str = null;    
	           while ((str = bufferedReader.readLine()) != null) {    
	               buffer.append(str);    
	           }    
	           bufferedReader.close();    
	           inputStreamReader.close();    
	           // 释放资源    
	           inputStream.close();    
	           inputStream = null;    
	           httpUrlConn.disconnect();    
	           jsonObject = JSONObject.fromObject(buffer.toString());    
	       } catch (ConnectException ce) {    
	        ce.printStackTrace();  
	          // log.error("Weixin server connection timed out.");    
	       } catch (Exception e) {    
	           //log.error("https request error:{}", e);   
	        e.printStackTrace();  
	       }    
	       return jsonObject;    
	   } 
	
	
	public static String requsetUrl(String urls) throws Exception{		
		BufferedReader br = null;
		String sTotalString= "";
		try{
			URL url = new URL(urls);
			URLConnection connection = url.openConnection();
			connection.setConnectTimeout(3000);
			connection.setDoOutput(true);
			String line = "";
			InputStream l_urlStream;
			l_urlStream = connection.getInputStream();
	
			br = new BufferedReader(new InputStreamReader(l_urlStream, "UTF-8"));
			while ((line = br.readLine()) != null) {
				sTotalString += line + "\r\n";
			}
		} finally {
			if(br!=null){
				try {
					br.close();
				} catch (IOException e) {
					br = null;
				}
			}
		}
		return sTotalString;
	}
}
