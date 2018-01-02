package com.kyl.ps.util;

/**
 * 
 * <p>
 * Title: Constants
 * </p>
 * <p>
 * Description: com.kyn.ps.common.constants
 * </p>
 * <p>
 * Copyright: Copyright (c) 2014
 * </p>
 * <p>
 * Company: Kyn
 * </p>
 * 
 * @author Jason.Guo
 * @date 2014-10-10
 */

public class Constants {

    public static final String COMMA_SPLITOR                    = ",";

    public static final String DATE_FORMAT_SPLITER              = "-";

    public static final String RESULT_ITEMS                        = "items";// 返回数据的list
    public static final String KEY_START                        = "start";// 起始页数
    public static final String RESULT_TOTAL             	    = "total";
    public static final int DEFAULT_KEY_START              	    = 1;
    public static final String KEY_MAXRESULT                    = "mr";// 每页显示数
    public static final int DEFAYLT_KEY_MAXRESULT               = 10;
    public static final int MAX_ROLLS               = 30000;//二维码贴纸最大卷数
    

    public static final String KEY_PAGE                         = "page";

    public static final String KEY_PRIMEID                      = "id";

    public static final String KEY_USERID                       = "uId";

    public static final String KEY_ISCOMBO                      = "isCombo";

    public static final String KEY_ISCOMBO_TRUE                 = "1";

    public static final String LOGIN_USER                       = "user";

    public static final String IP                               = "ip";

    public static final String DEFAULT_CHARSET                  = "UTF-8";

    public static final String SESSION_MESSAGE                  = "message";
    public static final String MESSAGE                  = "message";

    public static final String SESSION_MESSAGE_RESULTSMAP       = "message.resultsMap";

    public static final String REFERER_PAGE_URL                 = "url";

    public static final String USER_USERID                      = "uid";

    public static final String QUESTION_ID                      = "qid";

    public static final String HTTP_METHOD_POST                 = "POST";

    public static final String HTTP_METHOD_GET                  = "GET";

    public static final String TOTAL                            = "total";

    public static final String STATUS                           = "status";

    public static final String AREA                             = "area";

    public static final String FID                              = "fid";

    public static final String DATA                             = "data";

    public static final String CALL_PARAM_JSON_NAME             = "json";

    public static final String ROLE_LIST                        = "roleList";

    public static final String SESSION_COUNT                    = "count";

    public static final String USER_OPERATION                   = "uo";

    public static final String USER_OPERATION_INSERT            = "0";

    public static final String USER_OPERATION_QUERY             = "1";

    public static final String USER_OPERATION_UPDATE            = "2";

    public static final String USER_OPERATION_DELETE            = "3";

    public static final String CREATED_DATE                     = "createdDate";

    public static final String CREATED_UID                      = "createdUid";

    public static final String CREATED_USERNAME                 = "createdUsername";

    public static final String USER_RELATION_CREATED_UID        = "relationCreatedUid";

    public static final String USER_RELATION_CREATED_USERNAME   = "realtionCreatedUsername";

    public static final String UPDATED_DATE                     = "updatedDate";

    public static final String USER_UPDATED_UID                 = "updatedUid";

    public static final String USER_UPDATED_USERNAME            = "updatedUsername";

    public static final String RELAITON_UPDATED_DATE            = "relationUpdatedDate";

    public static final String USER_RELATION_UPDATED_UID        = "relationUpdatedUid";

    public static final String USER_RELATION_UPDATED_USERNAME   = "relationUpdatedUsername";

    public static final String SESSION_ACCOUNT                  = "account";

    public static final String SESSION_FILE                     = ".\\count.txt";

    public static final String ORIGINALPRODUCT_PREFIX           = "1";

    public static final String FACTORYPROCESS_PREFIX            = "2";

    public static final String TRANSPORT_PREFIX                 = "3";

    public static final String URL_ADD                          = "c=1";

    public static final String URL_UPDATE                       = "u=1";

    public static final String URL_DELETE                       = "d=1";

    public static final String URL_VIEW                         = "r=1";

    public static final String URL_OTHER                        = "o=1";

    public static final String URL_VERIFY                       = "v=1";

    public static final String URL_TASK                         = "t=1";

    public static final String URL_AUDIT                        = "e=1";

    public static final String JSON_ADD                         = "c:%s,";

    public static final String JSON_UPDATE                      = "u:%s,";

    public static final String JSON_DELETE                      = "d:%s,";

    public static final String JSON_VIEW                        = "r:%s,";

    public static final String JSON_OTHER                       = "o:%s,";

    public static final String JSON_VERIFY                      = "v:%s,";

    public static final String JSON_TASK                        = "t:%s,";

    public static final String JSON_AUDIT                       = "e:%s,";

    public static final String PRODUCT_SEARCH_TYPE_KEY          = "st";

    public static final String PRODUCT_SEARCH_TYPE_S            = "search";

    public static final String PRODUCT_SEARCH_TYPE_C            = "catalog";

    public static final String PRODUCT_SEARCH_TYPE_L            = "column";

    public static final String PRODUCT_SEARCH_SORT              = "sort";

    public static final String PRODUCT_SEARCH_SORT_TEMPORARY    = "sortStr";

    public static final String PRODUCT_SEARCH_KEYWORD           = "keyword";

    public static final String PRODUCT_SEARCH_KEYWORD_TEMPORARY = "keywords";

    public static final int    DEFAULT_PAGE_SIZE                = 10;

    public static final int    MAX_PAGE_SIZE                    = 50;

    public static final String SESSION_USER_ID                  = "userId";

    public static final String DEFAULT_SELL_TIME                = "2099-12-31 23:59:59";

    // message

    public static final String MESSAGE_SEND_BY_SMS              = "0";

    public static final String MESSAGE_SEND_BY_MMS              = "1";

    public static final String MESSAGE_EXTCODE                  = "extcode";

    public static final String MESSAGE_REQDELIVERYREPORT        = "reqdeliveryreport";

    public static final String MESSAGE_MSGFMT                   = "msgfmt";

    public static final String MESSAGE_SENDMETHOD               = "sendmethod";

    public static final String MESSAGE_DESTADDR                 = "destaddr";

    public static final String MESSAGE_DESTINATION              = "destination";

    public static final String MESSAGE_MESSAGECONTENT           = "messagecontent";

    public static final String MESSAGE_MESSAGEBODY              = "message";

    public static final String MESSAGE_REQUESTTIME              = "requesttime";

    public static final String MESSAGE_APPLICATIONID            = "applicationid";

    public static final String MESSAGE_SISMSID                  = "sismsid";

    // user
    public static final String USER_CREATEDUID                  = "createdUid";

    // plan
    public static final String PLAN_DATE                        = "date";

    public static final String PLAN_YEAR                        = "year";
    public static final String PLAN_START_YEAR                  = "startYear";
    public static final String PLAN_END_YEAR                    = "endYear";

    public static final String PLAN_MONTH                       = "month";
    public static final String PLAN_START_MONTH                 = "startMonth";
    public static final String PLAN_END_MONTH                   = "endMonth";

    public static final String PLAN_DAY                         = "day";
    public static final String PLAN_START_DAY                   = "startDay";
    public static final String PLAN_END_DAY                     = "endDay";

    public static final String PLAN_HOUR                        = "hour";
    public static final String PLAN_start_HOUR                  = "startHour";
    public static final String PLAN_end_HOUR                    = "endHour";

    public static final String PLAN_MINUTE                      = "minute";
    public static final String PLAN_START_MINUTE                = "startMinute";
    public static final String PLAN_END_MINUTE                  = "endMinute";

    public static final String PLAN_SECOND                      = "second";
    public static final String PLAN_START_SECOND                = "startSecond";
    public static final String PLAN_END_SECOND                  = "endSecond";

    public static final String USER_RELATIONUID                 = "relationUid";

    public static final String USER_USERNAME                    = "username";

    public static final String USER_RELATIONUNAME               = "relationUsername";

    public static final String RELATION_RELATIONAID             = "relationAid";

    public static final String AID                              = "aid";

    public static final String USER_UIDS                        = "uids";

    public static final String ATTACHMENT_PATH                  = "path";

    public static final String SYSTEM_CODE_DOCUMENT             = "0";

    public static final String USER_RELATIONSTATUS              = "relationStatus";

    // 已收
    public static final String STATUS_CC                        = "5";

    public static final String STATUS_RECEIVE                   = "2";

    public static final String STATUS_SEND                      = "1";

    public static final String REALPATH                         = "realPath";

    public static final String USER_CIDS                        = "cids";

    public static final String RELATION_RELATIONAREA            = "relationArea";

    public static final String USER_EXCEPT_USERID               = "eUserId";

    public static final String PLAN_EMPLOYEE                    = "employee";

    public static final String PLAN_IS_EMPLOYEE                 = "1";

    // constant
    public static final String CONSTANT_DATA_PLATFORM           = "001";

    public static final String STATUS_OK                        = "0";

    public static final String STATUS_ERROR                     = "1";

    public static final String STATUS_OUT_DATE                  = "-1";

    // 未审核词库的状态
    public static final String NOCHECK_WORD                     = "2";
    // 已审核词库的状态
    public static final String CHECK_WORD                       = "0";
    // 删除词库的状态
    public static final String DELETE_WORD                      = "1";

    public static enum PLATFORM {
        amazon, gome, jd, paipai, tmall
    };

    public static enum MONITOR_TYPE {
        client_heart, client_mongo_today, client_mongo_sum, client_craw_sum, client_craw_keyword, client_craw_backlog, client_craw_platform, model_speed_sum, model_speed_platform, index_product_heart, index_tag_heart, index_u_heart, index_heart, index_execute
    };

    public static final String MONITOR_KEY = "monitorType";

    // 词库分类类型
    public static final String BRAND       = "brand";
    public static final String BRANDNAME   = "brandName";
    public static final String COLOR       = "color";
    public static final String UNIT        = "unit";
    public static final String ALL         = "all";

    public static final String MONGO_NIN[] = new String[] { "wisdom", "fullsite", "usite", "preferential", "jd", "taobao", "tmall", "gome", "paipai",
            "amazon", ""};

    public static final String URL_REGEX   = "^(http|https)\\://([a-zA-Z0-9\\.\\-]+(\\:[a-zA-"
                                                   + "Z0-9\\.&%\\$\\-]+)*@)?((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{"
                                                   + "2}|[1-9]{1}[0-9]{1}|[1-9])\\.(25[0-5]|2[0-4][0-9]|[0-1]{1}"
                                                   + "[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\\.(25[0-5]|2[0-4][0-9]|"
                                                   + "[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\\.(25[0-5]|2[0-"
                                                   + "4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|([a-zA-Z0"
                                                   + "-9\\-]+\\.)*[a-zA-Z0-9\\-]+\\.[a-zA-Z]{2,4})(\\:[0-9]+)?(/"
                                                   + "[^/][a-zA-Z0-9\\.\\,\\?\\'\\\\/\\+&%\\$\\=~_\\-@]*)*$"; // URL验证正则表达式
}
