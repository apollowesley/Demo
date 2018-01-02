package com.kyl.ps.exception;


import java.util.HashMap;
import java.util.Map;

public class ExceptionCode {
	public static final Map<String, String> exceptions = new HashMap<String, String>();

	public void init() {
		ExceptionCode.exceptions.put(ExceptionCode.UNKOWN_EXCEPTION_CODE,
				"java.lang.Exception");
		ExceptionCode.exceptions.put(ExceptionCode.JSON_EXCEPTION_CODE,
				"com.soarsky.ps.common.exception.JSONException");
		ExceptionCode.exceptions.put(ExceptionCode.DB_EXCEPTION_CODE,
				"com.soarsky.ps.common.exception.DBException");
		ExceptionCode.exceptions.put(ExceptionCode.NOTLOGIN_EXCEPTION_CODE,
				"com.soarsky.ps.common.exception.NotLoginException");
		ExceptionCode.exceptions
				.put(ExceptionCode.APPNOTAVAILABLE_EXCEPTION_CODE,
						"com.soarsky.ps.common.exception.AppNotAvailableException");
		ExceptionCode.exceptions
				.put(ExceptionCode.APPNOTDOWNLOADBYUSER_EXCEPTION_CODE,
						"com.soarsky.ps.common.exception.AppNotDownloadByUserException");
		ExceptionCode.exceptions
				.put(ExceptionCode.APPCOMMENTEDBYUSER_EXCEPTION_CODE,
						"com.soarsky.ps.common.exception.AppCommentedByUserException");
		ExceptionCode.exceptions.put(
				ExceptionCode.GENERATIONHHTML_EXCEPTION_CODE,
				"com.soarsky.ps.common.exception.GenerateHtmlException");
		ExceptionCode.exceptions.put(ExceptionCode.LSSSERVER_EXCEPTION_CODE,
				"com.soarsky.ps.common.exception.LssServerException");
		ExceptionCode.exceptions.put(ExceptionCode.XMLCONVERT_EXCEPTION_CODE,
				"com.soarsky.ps.common.exception.XmlException");
		ExceptionCode.exceptions.put(ExceptionCode.CANNOT_PURCHASE_CODE,
				"com.soarsky.ps.common.exception.CannotPurchaseException");
		ExceptionCode.exceptions
				.put(ExceptionCode.APPFAVORITEBYUSER_EXCEPTION_CODE,
						"com.soarsky.ps.common.exception.AppFavoriteByUserException");
		ExceptionCode.exceptions.put(
				ExceptionCode.NOTFOUNDORDER_EXCEPTION_CODE,
				"com.soarsky.ps.common.exception.NotFoundOrderException");
		ExceptionCode.exceptions
				.put(ExceptionCode.TOOMANYDOWNLOAD_EXCEPTION_CODE,
						"com.soarsky.ps.common.exception.TooManyDownloadException");
		ExceptionCode.exceptions.put(ExceptionCode.MUSTPURCHASE_EXCEPTION_CODE,
				"com.soarsky.ps.common.exception.MustPurchaseException");
		ExceptionCode.exceptions.put(
				ExceptionCode.NOTORDEREXCEPTION_EXCEPTION_CODE,
				"com.soarsky.ps.common.exception.NotOrderException");
		ExceptionCode.exceptions.put(
				ExceptionCode.CANNOTDOWNLOAD_EXCEPTION_CODE,
				"com.soarsky.ps.common.exception.CanNotDownloadException");
		ExceptionCode.exceptions
				.put(ExceptionCode.BINDWEBOUSERFAILURE_EXCEPTION_CODE,
						"com.soarsky.ps.common.exception.BindWeboUserFailureException");
	};

	

	public static Exception getException(String key) {
		String exception = exceptions.get(key) == null ? "java.lang.Exception"
				: exceptions.get(key);
		try {
			return (Exception) Class.forName(exception).newInstance();
		} catch (InstantiationException e) {
			e.printStackTrace();
			return new Exception(ExceptionCode.UNKOWN_EXCEPTION_CODE);
		} catch (IllegalAccessException e) {
			e.printStackTrace();
			return new Exception(ExceptionCode.UNKOWN_EXCEPTION_CODE);
		} catch (ClassNotFoundException e) {
			e.printStackTrace();
			return new Exception(ExceptionCode.UNKOWN_EXCEPTION_CODE);
		}
	}

	/**
	 * 未知错误
	 */
	public static final String UNKOWN_EXCEPTION_CODE = "10000";
	public static final String UNKOWN_EXCEPTION_REASON = "未知错误";

	/**
	 * json转换抛错
	 */
	public static final String JSON_EXCEPTION_CODE = "10001";
	public static final String JSON_EXCEPTION_REASON = "json转换抛错";

	/**
	 * 数据库抛错
	 */
	public static final String DB_EXCEPTION_CODE = "10002";
	public static final String DB_EXCEPTION_REASON = "数据库抛错";

	/**
	 * 用户未登录
	 */
	public static final String NOTLOGIN_EXCEPTION_CODE = "10003";
	public static final String NOTLOGIN_EXCEPTION_REASON = "用户未登录";

	/**
	 * 该应用已下架
	 */
	public static final String APPNOTAVAILABLE_EXCEPTION_CODE = "10004";
	public static final String APPNOTAVAILABLE_EXCEPTION_REASON = "该应用已下架";

	/**
	 * 用戶未下载过该应用
	 */
	public static final String APPNOTDOWNLOADBYUSER_EXCEPTION_CODE = "10005";
	public static final String APPNOTDOWNLOADBYUSER_EXCEPTION_REASON = "用戶未下载过该应用";

	/**
	 * 用戶已评论过该应用
	 */
	public static final String APPCOMMENTEDBYUSER_EXCEPTION_CODE = "10006";
	public static final String APPCOMMENTEDBYUSER_EXCEPTION_REASON = "用戶已评论过该应用";

	/**
	 * 生产html
	 */
	public static final String GENERATIONHHTML_EXCEPTION_CODE = "10007";
	public static final String GENERATIONHHTML_EXCEPTION_REASON = "生成HTML错误";

	/**
	 * 链接lss服务器出错
	 */
	public static final String LSSSERVER_EXCEPTION_CODE = "10008";
	public static final String LSSSERVER_EXCEPTION_REASON = "链接Lss服务器出错";

	/**
	 * 链接lss服务器出错
	 */
	public static final String XMLCONVERT_EXCEPTION_CODE = "10009";
	public static final String XMLCONVERT_EXCEPTION_REASON = "转换xml错误";

	/**
	 * 购买不合法,已经存在相同的购买记录或者购买后下载次数未超过最大
	 */
	public static final String CANNOT_PURCHASE_CODE = "10010";
	public static final String CANNOT_PURCHASE_REASON = "您已经购买过该应用,请到详情页面下载";

	/**
	 * 不能重复收藏同一个应用
	 */
	public static final String APPFAVORITEBYUSER_EXCEPTION_CODE = "10011";
	public static final String APPFAVORITEBYUSER_EXCEPTION_REASON = "不能重复收藏同一个应用";

	/**
	 * 没有找到对应的订单
	 */
	public static final String NOTFOUNDORDER_EXCEPTION_CODE = "10012";
	public static final String NOTFOUNDORDER_EXCEPTION_REASON = "没有找到对应的订单";

	/**
	 * 下载次数过多,请重新购买
	 */
	public static final String TOOMANYDOWNLOAD_EXCEPTION_CODE = "10013";
	public static final String TOOMANYDOWNLOAD_EXCEPTION_REASON = "下载次数过多,请重新购买";

	/**
	 * 请选购买
	 */
	public static final String MUSTPURCHASE_EXCEPTION_CODE = "10014";
	public static final String MUSTPURCHASE_EXCEPTION_REASON = "请选购买";

	/**
	 * 没有找到对应订单信息
	 */
	public static final String NOTORDEREXCEPTION_EXCEPTION_CODE = "10015";
	public static final String NOTORDEREXCEPTION_EXCEPTION_REASON = "没有找到对应订单信息";

	/**
	 * 应用不能被下载
	 */
	public static final String CANNOTDOWNLOAD_EXCEPTION_CODE = "10016";
	public static final String CANNOTDOWNLOAD_EXCEPTION_REASON = "应用不能被下载";

	public static final String BINDWEBOUSERFAILURE_EXCEPTION_CODE = "10017";
	public static final String BINDWEBOUSERFAILURE_EXCEPTION_REASON = "绑定微博账户失败";
	
	public static final String NOTBINDEDWEIBOUSER_EXCEPTION_CODE = "10018";
	public static final String NOTBINDEDWEIBOUSER_EXCEPTION_REASON = "没有绑定微博用户";
	
	public static final String UPDATESTATUSFAILURE_EXCEPTION_CODE = "10019";
	public static final String UPDATESTATUSFAILURE_EXCEPTION_REASON = "发表评论到微博失败";
	
	public static final String CANNOTGETCOMMENT_EXCEPTION_CODE = "10020";
	public static final String CANNOTGETCOMMENT_EXCEPTION_REASON = "不能获取评论";
	
	public static final String EMAIL_ERROR_EXCEPTION_CODE = "10021";
	public static final String EMAIL_ERROR_EXCEPTION_REASON = "邮箱错误";
	
	public static final String PHONE_ERROR_EXCEPTION_CODE = "10022";
	public static final String PHONE_ERROR_EXCEPTION_REASON = "手机号码错误";
	
	public static final String CLEAN_MEMCAHED_ERROR_EXCEPTION_CODE = "10023";
	public static final String CLEAN_MEMCAHED_ERROR_EXCEPTION_REASON = "Clean memcached failure";
	
	public static final String USER_ADDED_EXCEPTION_CODE = "10024";
	public static final String USER_ADDED_EXCEPTION_REASON = "用户已经举报过该应用";
	
	public static final String NOT_DATA_EXCEPTION_CODE = "10025";
	public static final String NOT_DATA_EXCEPTION_REASON = "没有相应数据";
	
	public static final String SEARCH_ERROR_EXCEPTION_CODE = "10026";
	public static final String SEARCH_ERROR_EXCEPTION_REASON = "没有搜到相应数据";
	
	public static final String PAID_EXCEPTION_CODE = "10027";
	public static final String PAID_EXCEPTION_REASON = "您已经购买过该应用。";
	
	public static final String DOWNLOAD_LIMITED_EXCEPTION_CODE = "10028";
	public static final String DOWNLOAD_LIMITED_EXCEPTION_REASON = "该应用下载次数超过最大下载次数";
	
        public static final String NOT_ENOUGH_PRIVILEGE_EXCEPTION_CODE = "10029";
        public static final String NOT_ENOUGH_PRIVILEGE_EXCEPTION_REASON = "没有足够的权限";

}
