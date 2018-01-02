package download;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

/**
 * 网络工具类
 * @author wyshenzhongwei@chinabank.com.cn
 *
 */
public abstract class WebUtils {

    private static final String DEFAULT_CHARSET = "UTF-8";
    private static final String METHOD_POST     = "POST";
    private static final int BUFFER_SIZE = 1024;

    private WebUtils() {
    }

    /**
     * 执行下载文件请求。
     * 
     * @param url 请求地址
     * @param params 请求参数
     * @param filename 存储路径（带文件名）
     * @throws IOException
     */
    public static void download(String url, Map<String, String> params, int connectTimeout,
                                int readTimeout,String filename) throws IOException {
        doPost(url, params, DEFAULT_CHARSET, connectTimeout, readTimeout,filename);
    }

    /**
     * 执行HTTP POST请求。
     * 
     * @param url 请求地址
     * @param params 请求参数
     * @param charset 字符集，如UTF-8, GBK, GB2312
     * @return 响应字符串
     * @throws IOException
     */
    private static void doPost(String url, Map<String, String> params, String charset,
                                int connectTimeout, int readTimeout,String filename) throws IOException {
        String query = buildQuery(params, charset);
        byte[] content = {};
        if (query != null) {
            content = query.getBytes(charset);
        }
        doPost(url, content, connectTimeout, readTimeout,filename);
    }

    /**
     * 执行HTTP POST请求。
     * 
     * @param url 请求地址
     * @param ctype 请求类型
     * @param content 请求字节数组
     * @return 响应字符串
     * @throws IOException
     */
    private static void doPost(String urlstr, byte[] content, int connectTimeout,
                                int readTimeout,String filename) throws IOException{
    	HttpURLConnection conn = null;
    	OutputStream out = null;
        try {
        	URL url = new URL(urlstr);
        	conn = (HttpURLConnection)url.openConnection();
        	conn.setRequestMethod(METHOD_POST);
        	conn.setConnectTimeout(connectTimeout);
        	conn.setReadTimeout(readTimeout);
        	conn.setDoInput(true);
        	conn.setDoOutput(true);
            out = conn.getOutputStream();
            out.write(content);
            saveFile(conn,filename);
        } finally {
            if (out != null) {
                out.close();
            }
            if (conn != null) {
                conn.disconnect();
            }
        }

    }
    
    private static void saveFile(HttpURLConnection conn,String filename) throws IOException{
        byte[] buf = new byte[BUFFER_SIZE];  
        int size = 0;  
  
        //建立文件  
        File file = new File(filename);  
        if(!file.exists()) {  
            if(!file.getParentFile().exists()) {  
                file.getParentFile().mkdirs();  
            }  
            file.createNewFile();  
        }  

        //文件输出流
        FileOutputStream fos = new FileOutputStream(filename);
        
        //获取网络输入流  
        BufferedInputStream bis = new BufferedInputStream(conn.getInputStream());
        
        System.out.println("POST " + conn.getURL() + " " + conn.getHeaderField(0));
        System.out.println("Content-Length:" + conn.getHeaderField("Content-Length"));
        String returnCode = conn.getHeaderField("Return-Code");
        System.out.println("Return-Code:" + (returnCode==null?"0000":returnCode));
  
        //保存文件  
        while ((size = bis.read(buf)) != -1)  
            fos.write(buf, 0, size);  
  
        fos.close();  
        bis.close();  
    }
    
    private static String buildQuery(Map<String, String> params, String charset) throws IOException {
        if (params == null || params.isEmpty()) {
            return null;
        }

        StringBuilder query = new StringBuilder();
        Set<Entry<String, String>> entries = params.entrySet();
        boolean hasParam = false;

        for (Entry<String, String> entry : entries) {
            String name = entry.getKey();
            String value = entry.getValue();
            // 忽略参数名或参数值为空的参数
            if (StringUtils.areNotEmpty(name, value)) {
                if (hasParam) {
                    query.append("&");
                } else {
                    hasParam = true;
                }

                query.append(name).append("=").append(URLEncoder.encode(value, charset));
            }
        }

        return query.toString();
    }

}
