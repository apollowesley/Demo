package https_test;

import java.security.cert.CertificateException;  
import java.security.cert.X509Certificate;  
  
import javax.net.ssl.X509TrustManager;  
  
/**  
 * 证书信任管理器（用于https请求）  
 * @date 2013-08-08  
 */  
public class MyX509TrustManager implements X509TrustManager{  
  
      
    public void checkClientTrusted(X509Certificate[] arg0, String arg1)  
            throws CertificateException {  
          
          
    }  
  
      
    public void checkServerTrusted(X509Certificate[] arg0, String arg1)  
            throws CertificateException {  
          
          
    }  
  
      
    public X509Certificate[] getAcceptedIssuers() {  
          
        return null;  
    }  
  
}  