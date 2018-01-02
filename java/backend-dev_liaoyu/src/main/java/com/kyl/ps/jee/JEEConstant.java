package com.kyl.ps.jee;

/**
 * 常量 定义J2EE常量
 * 
 * @author xiaoliao
 */
public interface JEEConstant {

    public static String       SESSION_LOGIN_TOKEN     = "session.security.user";

    public static final String SESSION_RANDNUMBER      = "session.randNumber";

    public static String       SESSION_MODULE          = "session.module";

    public static String       SESSION_MODULE_MENU     = "session.module.menu";

    public static String       SESSION_MODULE_CUR      = "session.module.cur";

    public static String       SESSION_MODULE_MENU_CUR = "session.module.menu.cur";

    public static String       BREADCRUMB              = "breadcrumb";
    public static String       MANAGER_USER_ID              = "managerUserId_";
    public static String       MANAGER_USER_NAME              = "managerUserName_";

    /**
     * 重复提交token
     */
    public static final String SUBMIT_TOKEN            = "token_";

    public static final String SUBMIT_TOKEN_HISTORY    = "token_history_";

    public static final String PRIMRYID                = "uuid";

    public static final String STATUS                  = "status";

    public static final String STATUS_OK               = "0";

    public static final String STATUS_ERROR            = "1";

    public static final String STATUS_OUT_DATE         = "-1";
    
    public static final String MESSAGE = "message";
    
    public static final String REQUEST_DATE="request_date";

}
