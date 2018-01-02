package com.kyl.ps.interfaces.controller.impl;

import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.image.BufferedImage;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

import javax.imageio.ImageIO;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.lang.Validate;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.servlet.ModelAndView;
import org.springframework.web.servlet.view.RedirectView;

import com.kyl.ps.exception.GenerateHtmlException;
import com.kyl.ps.infrastructure.service.impl.manageruser.ManagerUserServiceImpl;
import com.kyl.ps.interfaces.controller.AbstractController;
import com.kyl.ps.model.config.CustomMenu;
import com.kyl.ps.model.config.ModuleMenu;
import com.kyl.ps.pojo.BaseInputMessage;
import com.kyl.ps.pojo.BaseReturnMessage;
import com.kyl.ps.util.BeanHolder;
import com.kyl.ps.util.Constants;
import com.kyl.ps.util.MD5Util;

/**
 * <p>Title: HomeController.java</p>
 * <p>Description: com.kyl.ps.interfaces.controller.impl</p>
 * <p>Copyright: Copyright (c) 2014</p>
 * <p>Company: Kyl</p>
 * @author: xiaoliao
 * @date:   2014年11月17日
 *
 */
@Controller
@RequestMapping("/home/*")
public class HomeController extends AbstractController{
	
	private static final Logger log = Logger.getLogger(HomeController.class);
	@Autowired
	 ManagerUserServiceImpl managerUserServiceImpl;
	
	
	
	
	@RequestMapping(value="/clearData",method=RequestMethod.GET)
	public void clearData(HttpServletRequest request,
			HttpServletResponse response) throws Exception {
		Map<String, Object> returnMap = new HashMap<String, Object>();
		try {
			log.info("清除缓存map...");
			if(null != MANAGER_USER && MANAGER_USER.size() > 0){
				MANAGER_USER.clear();
			}
			if(null != USER_ACCOUNT && USER_ACCOUNT.size() > 0){
				USER_ACCOUNT.clear();
			}
			if(null != USER_EXTEND && USER_EXTEND.size() > 0){
				USER_EXTEND.clear();
			}
			if(null != DICT_GARDEN && DICT_GARDEN.size() > 0){
				DICT_GARDEN.clear();
			}
			if(null != RECYCLER && RECYCLER.size() > 0){
				RECYCLER.clear();
			}
			if(null != CREATIONS && CREATIONS.size() > 0){
				CREATIONS.clear();
			}
			returnMap.put(Constants.STATUS, Constants.STATUS_OK);
			returnMap.put(Constants.MESSAGE, "调用成功");
		} catch (Exception e) {
			if (returnMap.size() == 0) {
				e.printStackTrace();
				returnMap.put(Constants.STATUS, 500);
				returnMap.put(Constants.MESSAGE, "服务器异常");
			}
		}
		writeJson(response, returnMap);
	}
	
	
	/**
	 * 
	 * @Description：进入到系统首页
	 * @author: xiaoliao
	 * @date:   2014年11月18日
	 *
	 * @param request
	 * @param response
	 * @return
	 * @throws GenerateHtmlException 
	 */
	@RequestMapping(value="/index",method=RequestMethod.GET)
    public ModelAndView index(HttpServletRequest request, HttpServletResponse response) throws GenerateHtmlException  { 

		ModelAndView model = new ModelAndView();
		model.setViewName("login");// 首页跳转
    	return model;
	} 
	
	/**
	 * 
	 * @Description：系统欢迎页
	 * @author: xiaoliao
	 * @date:   2015年1月21日
	 *
	 * @param request
	 * @param response
	 * @return
	 * @throws GenerateHtmlException
	 */
	@RequestMapping(value="/welcome",method=RequestMethod.GET)
    public ModelAndView welcome(HttpServletRequest request, HttpServletResponse response) throws GenerateHtmlException  { 

		ModelAndView model = new ModelAndView();
		model.setViewName("welcome");
        
    	return model;
	} 
	
	public static void main(String[] args) {
		System.out.println(BeanHolder.getMessage("common.error.message.repeat.submit"));
	}
	/**
	 * 
	 * @Description：登录
	 * @author: xiaoliao
	 * @date:   2014年11月18日
	 *
	 * @param request
	 * @param response
	 * @return
	 * @throws GenerateHtmlException 
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value="/login",method=RequestMethod.POST)
    public ModelAndView login(HttpServletRequest request, HttpServletResponse response) throws GenerateHtmlException  { 

		BaseInputMessage inMessage = new BaseInputMessage();
        BaseReturnMessage outMessage = new BaseReturnMessage();
        
        ModelAndView model = new ModelAndView();
        
        try {
        	this.createCondition(inMessage, request);
        	System.out.println("====================");
        	//验证数据
			Validate.notEmpty(inMessage.getRequestMap().get("username").toString(), "reqest.param.empty");
			Validate.notEmpty(inMessage.getRequestMap().get("password").toString(), "reqest.param.empty");
			Validate.notEmpty(inMessage.getRequestMap().get("vecode").toString(), "reqest.param.empty");

			model.addObject("username", inMessage.getRequestMap().get("username").toString());
			
        	if (!inMessage.getRequestMap().get("vecode").toString()
							.equals(request.getSession(false).getAttribute(SESSION_RANDNUMBER))) {
				model.addObject("error", "账号或密码不正确");
				model.setViewName("login");
			}else {
				inMessage.getRequestMap().put("pwd", MD5Util.getMd5Str(inMessage.getRequestMap().get("password").toString()));
				//登录验证
				Map<String,Object> map = managerUserServiceImpl.queryManagerUser(inMessage);
				if (null == map || map.size() == 0) {
					model.addObject("error", BeanHolder.getMessage(outMessage.getResultStr()));
					model.setViewName("login");
				} else {
					request.getSession(false).setAttribute(SESSION_LOGIN_TOKEN, map);
//					request.getSession(false).setAttribute(SESSION_MODULE, (List<ModuleMenu>)outMessage.getResultsMap().get("modules"));
					model.setViewName("home");
				}
			}
        	
        } catch (Exception e) {
//            e.printStackTrace();
            throw new GenerateHtmlException(e.getMessage());  
        }
    	
    	return model;
	} 
	
	/**
	 * 
	 * @Description：退出登录
	 * @author: xiaoliao
	 * @date:   2014年12月19日
	 *
	 * @param request
	 * @param response
	 * @return
	 * @throws GenerateHtmlException
	 */
	@RequestMapping(value="/loginout",method=RequestMethod.GET)
    public ModelAndView loginOut(HttpServletRequest request, HttpServletResponse response) throws GenerateHtmlException  { 

		request.getSession(false).invalidate();
//		request.getSession(false).removeAttribute(SESSION_LOGIN_TOKEN);
//		request.getSession(false).removeAttribute(SESSION_MODULE);
//		request.getSession(false).removeAttribute(SESSION_MODULE_MENU);
//		request.getSession(false).removeAttribute(SESSION_MODULE_CUR);
//		request.getSession(false).removeAttribute(SESSION_MODULE_MENU_CUR);
		
        return new ModelAndView(new RedirectView("index"));
	} 
	
	/**
	 * 
	 * @Description：生成验证码
	 * @author: xiaoliao
	 * @date:   2014年12月19日
	 *
	 * @param request
	 * @param response
	 * @throws javax.servlet.ServletException
	 * @throws java.io.IOException
	 */
	@RequestMapping(value="/randnumberimage",method=RequestMethod.GET)
	public void showImage(HttpServletRequest request,
			HttpServletResponse response)
			throws javax.servlet.ServletException, java.io.IOException {
		response.setHeader("Pragma", "No-cache");
		response.setHeader("Cache-Control", "no-cache");
		response.setDateHeader("Expires", 0);
		response.setHeader("Content-Type", "image/jpeg");

		int width = 50, height = 25;
		System.setProperty("java.awt.headless", "true");
		BufferedImage image = new BufferedImage(width, height,
				BufferedImage.TYPE_INT_RGB);

		Graphics g = image.getGraphics();

		Random random = new Random();

		g.setColor(new Color(192, 174, 231));
		g.fillRect(0, 0, width, height);

		g.setColor(Color.white);

		g.setFont(new Font("Times New Roman", Font.BOLD, 17));

		g.setColor(getRandColor(60, 120));

		for (int i = 0; i < 10; i++) {
			int x = random.nextInt(width);
			int y = random.nextInt(height);
			int xl = random.nextInt(12);
			int yl = random.nextInt(12);
			g.drawLine(x, y, x + xl, y + yl);
		}

		StringBuilder sRand = new StringBuilder();
		for (int i = 0; i < 4; i++) {
			sRand.append(random.nextInt(10));
		}
		g.drawString(sRand.toString(), 5, 18);

		request.getSession(false).setAttribute(SESSION_RANDNUMBER, sRand.toString());

		g.dispose();
		ImageIO.write(image, "JPEG", response.getOutputStream());
	}

	/*
	 * 验证码图片颜色
	 */
	private Color getRandColor(int fc, int bc) {
		Random random = new Random();
		if (fc > 255)
			fc = 255;
		if (bc > 255)
			bc = 255;
		int r = fc + random.nextInt(bc - fc);
		int g = fc + random.nextInt(bc - fc);
		int b = fc + random.nextInt(bc - fc);
		return new Color(r, g, b);
	}
	
	/**
	 * 
	 * @Description：模块跳转
	 * @author: xiaoliao
	 * @date:   2015年1月5日
	 *
	 * @param request
	 * @param response
	 * @return
	 * @throws GenerateHtmlException
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value="/moduleswitch",method=RequestMethod.GET)
    public ModelAndView moduleSwitch(HttpServletRequest request, HttpServletResponse response) throws GenerateHtmlException  { 

		BaseInputMessage inMessage = new BaseInputMessage();
        BaseReturnMessage outMessage = new BaseReturnMessage();
        
        ModelAndView model = new ModelAndView();
        
        try {
        	this.createCondition(inMessage, request);
        	
        	//验证数据
			Validate.notEmpty(inMessage.getRequestMap().get("module").toString(), "module.empty");

			
			if (((List<ModuleMenu>)outMessage.getResult()).isEmpty()) {
				model.setViewName("login");
			}else {
				request.getSession(false).setAttribute(SESSION_MODULE_MENU, (List<ModuleMenu>)outMessage.getResult());	
	        	
				model.setViewName("index");
			}
			
        } catch (Exception e) {
            e.printStackTrace();
            throw new GenerateHtmlException(e.getMessage());  
        }
    	
    	return model;
	} 
	
	/**
	 * 
	 * @Description：图片管理自定义菜单模块跳转
	 * @author: xiaoliao
	 * @date:   2015年1月5日
	 *
	 * @param request
	 * @param response
	 * @return
	 * @throws GenerateHtmlException
	 */
	@SuppressWarnings("unchecked")
	@RequestMapping(value="/moduleforimage",method=RequestMethod.GET)
    public ModelAndView moduleForImage(HttpServletRequest request, HttpServletResponse response) throws GenerateHtmlException  { 

		BaseInputMessage inMessage = new BaseInputMessage();
        BaseReturnMessage outMessage = new BaseReturnMessage();
        
        ModelAndView model = new ModelAndView();
        
        try {
        	this.createCondition(inMessage, request);
        	
        	//验证数据
			Validate.notEmpty(inMessage.getRequestMap().get("module").toString(), "module.empty");

//			outMessage = moduleCustomMenuService.proess(inMessage);
			
			List<CustomMenu> menus = (List<CustomMenu>)outMessage.getResult();
			
			//如果用户没有上传过图片，提示错误
			if (menus.isEmpty()) {
				throw new GenerateHtmlException("image.page.label.error.faile");  
			}
			
			request.getSession(false).setAttribute(SESSION_MODULE_MENU, menus);	
        	
			model.setViewName("indexcustom");
			
        } catch (Exception e) {
            e.printStackTrace();
            throw new GenerateHtmlException(e.getMessage());  
        }
    	
    	return model;
	} 
	
}
