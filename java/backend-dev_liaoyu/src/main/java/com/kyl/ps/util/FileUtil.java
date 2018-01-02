package com.kyl.ps.util;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.regex.Pattern;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.aliyun.oss.OSSClient;
import org.springframework.web.multipart.MultipartFile;

public class FileUtil {
	public static String upload(MultipartFile file,HttpServletRequest request,HttpServletResponse response,String url) throws IOException {
		
		String tomcatRoot = request.getSession().getServletContext().getRealPath("/");
        String[] foo = tomcatRoot.split(Pattern.quote(File.separator));  
        StringBuilder tomcatWebAppsBuilder = new StringBuilder();  
        int i = 0;  
        for(String paths : foo){  
            ++i;  
            if(i != foo.length){  
                tomcatWebAppsBuilder.append(paths);  
                tomcatWebAppsBuilder.append(File.separator);  
            }  
        }  
        String tomcatWebApps = tomcatWebAppsBuilder.toString();
		response.setCharacterEncoding("utf-8");  
        PrintWriter out =  response.getWriter();
        // CKEditor提交的很重要的一个参数    
        String callback = request.getParameter("CKEditorFuncNum"); 
		/**一、验证*/
		//1 验证是否为空
		if(file.isEmpty()){
			out.print("<font color=\"red\" size=\"2\">*请选择上传文件</font>");  
			return null;  
        }
		//2 验证格式
		//获取文件的后缀名 上传文件名->file.getOriginalFilename()
		String expandedName = file.getOriginalFilename().split("\\.")[1];  //文件扩展名
		if (file.getContentType().equals("image/pjpeg") || file.getContentType().equals("image/jpeg")) {    
            //IE6上传jpg图片的headimageContentType是image/pjpeg，而IE9以及火狐上传的jpg图片是image/jpeg    
            expandedName = ".jpg";    
        }else if(file.getContentType().equals("image/png") || file.getContentType().equals("image/x-png")){    
            //IE6上传的png图片的headimageContentType是"image/x-png"    
            expandedName = ".png";    
        }else if(file.getContentType().equals("image/gif")){    
            expandedName = ".gif";    
        }else if(file.getContentType().equals("image/bmp")){    
            expandedName = ".bmp";    
        }else{
        	 out.println("<script type=\"text/javascript\">");      
             out.println("window.parent.CKEDITOR.tools.callFunction(" + callback + ",''," + "'文件格式不正确（必须为.jpg/.gif/.bmp/.png文件）');");     
             out.println("</script>");    
             return null;    
        }    
		
		//3 验证文件大小
		if(file.getSize() > 600*1024){ 
			out.println("<script type=\"text/javascript\">");      
            out.println("window.parent.CKEDITOR.tools.callFunction(" + callback + ",''," + "'文件大小不得大于600k');");     
            out.println("</script>");    
            return null;
		}    
		
		/**二、上传文件*/
		//1 以当前时间 创建目录并且重命名图片
		
		//获取并格式化当前时间
		SimpleDateFormat sdf=new SimpleDateFormat("yyyy-MM-dd");
		String nowTime = sdf.format(new Date());
				
		//2 获取上传到服务器的路径
//		String path = request.getSession().getServletContext().getRealPath("web"+File.separator+url);
		String path = tomcatWebApps + "ROOT" + File.separator + "webackend" + File.separator + url + File.separator;
		//3 创建目录
		createDir(path+=File.separator+nowTime);
		//4 采用时间+UUID的方式随即命名文件
		String imageName = java.util.UUID.randomUUID().toString()+expandedName;
		
		//5 开始上传
		FileOutputStream os  = null;
		InputStream is = null;
		try {
			os = new FileOutputStream(new File(path,imageName));
			is = file.getInputStream();
			byte[] buffer = new byte[1024];       
	        int length = 0;    
	        while ((length = is.read(buffer)) > 0) {       
	            os.write(buffer, 0, length);
	        } 
		} catch (Exception e) {
			e.printStackTrace();
		}finally{
			 try {
				os.flush();
				os.close();
				is.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
//		String basePath = request.getScheme()+"://"+request.getServerName()+":"+request.getServerPort()+request.getContextPath()+"/"+"web"+"/"+url+"/";
		String basePath = request.getScheme()+"://"+request.getServerName()+":"+request.getServerPort()+"/"+"webackend"+"/"+url+"/"+nowTime+"/"+imageName;		
		// 返回"图像"选项卡并显示图片    
	    out.println("<script type=\"text/javascript\">");      
	    out.println("window.parent.CKEDITOR.tools.callFunction(" + callback + ",'" + basePath + "','')");      
	    out.println("</script>");
		//返回新的文件名
		return nowTime+"/"+imageName;		
		
	}
	
public static String upload(MultipartFile file,HttpServletRequest request,HttpServletResponse response) throws IOException {
		
		response.setCharacterEncoding("utf-8");  
        PrintWriter out =  response.getWriter();
        // CKEditor提交的很重要的一个参数    
        String callback = request.getParameter("CKEditorFuncNum"); 
		/**一、验证*/
		//1 验证是否为空
		if(file.isEmpty()){
			out.print("<font color=\"red\" size=\"2\">*请选择上传文件</font>");  
			return null;  
        }
		//2 验证格式
		//获取文件的后缀名 上传文件名->file.getOriginalFilename()
		String expandedName = file.getOriginalFilename().split("\\.")[1];  //文件扩展名
		System.out.println(file.getContentType());
		if (file.getContentType().equals("image/pjpeg") || file.getContentType().equals("image/jpeg")) {    
            //IE6上传jpg图片的headimageContentType是image/pjpeg，而IE9以及火狐上传的jpg图片是image/jpeg    
            expandedName = ".jpg";    
        }else if(file.getContentType().equals("image/png") || file.getContentType().equals("image/x-png")){    
            //IE6上传的png图片的headimageContentType是"image/x-png"    
            expandedName = ".png";    
        }else if(file.getContentType().equals("image/gif")){    
            expandedName = ".gif";    
        }else if(file.getContentType().equals("image/bmp")){    
            expandedName = ".bmp";    
        }else{
        	 out.println("<script type=\"text/javascript\">");      
             out.println("window.parent.CKEDITOR.tools.callFunction(" + callback + ",''," + "'文件格式不正确（必须为.jpg/.gif/.bmp/.png文件）');");     
             out.println("</script>");    
             return null;    
        }    
		
		//3 验证文件大小
		if(file.getSize() > 600*1024){ 
			out.println("<script type=\"text/javascript\">");      
            out.println("window.parent.CKEDITOR.tools.callFunction(" + callback + ",''," + "'文件大小不得大于600k');");     
            out.println("</script>");    
            return null;
		}    
		
		/**二、上传文件*/
		//1 以当前时间 创建目录并且重命名图片
		
		//获取并格式化当前时间
		SimpleDateFormat sdf=new SimpleDateFormat("yyyy-MM-dd");
		String nowTime = sdf.format(new Date());
				
		//2 获取上传到服务器的路径
		String path = request.getSession().getServletContext().getRealPath("web/imgUpload");
		
		//3 创建目录
		createDir(path+="/"+nowTime);
		
		//4 采用时间+UUID的方式随即命名文件
		String imageName = java.util.UUID.randomUUID().toString()+expandedName;
		
		//5 开始上传
		FileOutputStream os  = null;
		InputStream is = null;
		try {
			os = new FileOutputStream(new File(path,imageName));
			is = file.getInputStream();
			byte[] buffer = new byte[1024];       
	        int length = 0;    
	        while ((length = is.read(buffer)) > 0) {       
	            os.write(buffer, 0, length);
	        } 
		} catch (Exception e) {
			e.printStackTrace();
		}finally{
			 try {
				os.flush();
				os.close();
				is.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
			
		String basePath = request.getScheme()+"://"+request.getServerName()+":"+request.getServerPort()+request.getContextPath()+"/web/imgUpload/";
		System.out.println(request.getServerName());
	    // 返回"图像"选项卡并显示图片    
	    out.println("<script type=\"text/javascript\">");      
	    out.println("window.parent.CKEDITOR.tools.callFunction(" + callback + ",'" + basePath + nowTime+"/"+imageName + "','')");      
	    out.println("</script>");
		//返回新的文件名
		return nowTime+"/"+imageName;		
		
	}
	
	// 创建目录
	 public static void createDir(String destDirName) {
	    File dir = new File(destDirName);
	    if (dir.exists()) return;
	    if (!dir.mkdirs()) return;
     }
     public static String getWebAppRealPath(){
		String  realPath = System.getProperty("searchbackend.root");
		return realPath;
	 }
	 public static void  deleteOSSFile(String key){
		 // endpoint以杭州为例，其它region请按实际情况填写
		 String endpoint = "oss-cn-shenzhen.aliyuncs.com";
		 // accessKey请登录https://ak-console.aliyun.com/#/查看
		 String accessKeyId = "LTAIKm16SvdURolO";
		 String accessKeySecret = "45cEC00EZjl8t6azSmrBOpj1RDIu1o";
		 // 创建OSSClient实例
		 OSSClient ossClient = new OSSClient(endpoint, accessKeyId, accessKeySecret);

		 // 删除Object
		 ossClient.deleteObject("diu-news-images", key);
		 // 关闭client
		 ossClient.shutdown();
	 }
	 public static  void main(String args[]){
			Map<String,Object> map = new HashMap<String,Object>();
			map.put("column_id",-1);
			System.out.println(map.get("column_id").equals((Object) (-1)));
	}
   }

