package https_test;

import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Properties;

import javax.net.ssl.HttpsURLConnection;

public class test extends httpsTest {

	public static void main(String[] args) throws Exception {
		// TODO Auto-generated method stub
		 // 创建URL对象
        Properties pps=System.getProperties();
        System.out.println(pps.getProperty("file.encoding"));
        URL myURL = new URL("https://www.sun.com");
        // 创建HttpsURLConnection对象，并设置其SSLSocketFactory对象
        HttpsURLConnection httpsConn = (HttpsURLConnection) myURL
                .openConnection();
        // 取得该连接的输入流，以读取响应内容
        InputStreamReader insr = new InputStreamReader(httpsConn
                .getInputStream());
        // 读取服务器的响应内容并显示
        int respInt = insr.read();
        while (respInt != -1) {
            System.out.print((char) respInt);
            respInt = insr.read();
        }
	}

}
