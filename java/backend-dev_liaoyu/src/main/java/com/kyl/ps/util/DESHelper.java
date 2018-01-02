package com.kyl.ps.util;

import java.security.Key;

import javax.crypto.Cipher;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.DESKeySpec;

import sun.misc.*;


public class DESHelper {
	public static final String ALGORITHM_DES = "DES";  
	
    private static final String keyContext="kylsearch";
    
    private Key key;
    
    private static final DESHelper desHelper=new DESHelper();
    
    public static DESHelper getInstance(){
    	return desHelper;
    }
    
    private  DESHelper(){
    	this.initKey(keyContext);
    }
    
	public String bytesToHexString(byte[] bs) {  
        StringBuffer sb = new StringBuffer();  
        String hex = "";  
        for (int i = 0; i < bs.length; i++) {  
            hex = Integer.toHexString(bs[i] & 0xFF);  
            if (hex.length() == 1) {  
                hex = '0' + hex;  
            }  
            sb.append(hex);  
        }  
        return sb.toString();  
    }  
    
    
	public String encrypt(String plainText) {  
        byte [] byteEncrypt = null ;  
        byte [] bytePlain = null ;  
        String strEncrypt = "" ;  
        BASE64Encoder base64en = new BASE64Encoder();  
        try {  
            bytePlain = plainText.getBytes("UTF-8");  
            byteEncrypt = encryptByte(bytePlain);  
            strEncrypt = base64en.encode(byteEncrypt);  
            strEncrypt=strEncrypt.replace("\r\n", "").replaceAll("\n", "");
        } catch (Exception e) {  
            throw new RuntimeException("encrypt error. Cause: " + e);  
        } finally {  
            base64en = null ;  
            bytePlain = null ;  
            byteEncrypt = null ;  
        }  
        return strEncrypt;  
     }
    
	public String decrypt(String encryptText) {  
        BASE64Decoder base64De = new BASE64Decoder();  
        byte [] bytePlainText = null ;  
        byte [] byteEncrypt = null ;  
        String plainText = "" ;  
        try {  
            byteEncrypt = base64De.decodeBuffer(encryptText);  
            bytePlainText = this.decryptByte(byteEncrypt);  
            plainText = new String(bytePlainText, "UTF-8" );  
        } catch (Exception e) {  
            throw new RuntimeException("decrypt error. Cause: " + e);  
        } finally {  
            base64De = null ;  
            bytePlainText = null ;  
            byteEncrypt = null ;  
        }  
        return plainText;  
     }  
    
    private byte [] encryptByte( byte [] bytes) {  
        byte [] byteFinal = null ;  
        Cipher cipher;  
        try {  
            cipher = Cipher.getInstance (ALGORITHM_DES);  
            cipher.init(Cipher.ENCRYPT_MODE , key );  
            byteFinal = cipher.doFinal(bytes);  
        } catch (Exception e) {  
            throw new RuntimeException("encrypt error. Cause: " + e);  
        } finally {  
            cipher = null ;  
        }  
        return byteFinal;  
     }  
    
    private byte [] decryptByte( byte [] byteD) {  
        Cipher cipher;  
        byte [] byteFinal = null ;  
        try {  
            cipher = Cipher.getInstance (ALGORITHM_DES);  
            cipher.init(Cipher.DECRYPT_MODE,key);  
            byteFinal = cipher.doFinal(byteD);  
        } catch (Exception e) {  
            throw new RuntimeException("decrypt error. Cause: " + e);  
        } finally {  
            cipher = null ;  
        }  
        return byteFinal;  
     }  
    
    public void initKey(String strKey) {  
        try {  
        	SecretKeyFactory keyFactory = SecretKeyFactory.getInstance(ALGORITHM_DES);
        	DESKeySpec keySpec = new DESKeySpec(strKey.getBytes());
    		keyFactory.generateSecret(keySpec);
    		this.key = keyFactory.generateSecret(keySpec);
        	
        } catch (Exception e) {  
            throw new RuntimeException("generate key error. Cause: " + e);  
        }  
     }
    
    public Key getKey(){
    	return this.key;
    }
    
    public static void main(String[] args) {
    	DESHelper desHelper = DESHelper.getInstance();
    	System.out.println(desHelper.encrypt("18701016199"));
	}
}  
  
