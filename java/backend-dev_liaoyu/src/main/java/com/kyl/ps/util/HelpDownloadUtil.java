package com.kyl.ps.util;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;

import javax.servlet.http.HttpServletResponse;


public class HelpDownloadUtil {
	
	public static void download(HttpServletResponse response,String fileName, String downLoadPath) throws Exception{
		response.setContentType("text/html;charset=UTF-8");  
		/**获取文件长度*/
		long fileLength = new File(downLoadPath).length();  
		response.setContentType("application/octet-stream");  
		response.setHeader("Content-disposition", "attachment; filename="  
		        + new String(fileName.getBytes("utf-8"), "ISO8859-1"));  
		response.setHeader("Content-Length", String.valueOf(fileLength));  
		try(BufferedInputStream bis = new BufferedInputStream(new FileInputStream(downLoadPath));
			BufferedOutputStream bos = new BufferedOutputStream(response.getOutputStream());) {
			byte[] buff = new byte[2048];  
			int bytesRead;  
			while (-1 != (bytesRead = bis.read(buff, 0, buff.length))) {  
			    bos.write(buff, 0, bytesRead);  
			    bos.flush();
			}
		}
	}
}
