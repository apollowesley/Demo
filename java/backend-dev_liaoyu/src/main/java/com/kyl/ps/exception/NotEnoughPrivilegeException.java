package com.kyl.ps.exception;


/**
 * 
 * <p>Title: OutOfRegisterTimeException</p>
 * <p>Description: com.soarsky.ps.common.exception</p>
 * <p>Copyright: Copyright (c) 2013</p>
 * <p>Company: Kyn</p>
 * @author    Jason.Guo
 * @date      2013-3-3
 */

public class NotEnoughPrivilegeException extends RuntimeException {
    private static final long serialVersionUID = 86589893088746022L;
    private String message;
    private int errorCode;

    public NotEnoughPrivilegeException(){}
    
    public NotEnoughPrivilegeException(int errorCode, String resourceKey) {
        this(errorCode, resourceKey, "");
    }

    public NotEnoughPrivilegeException(int errorCode, String resourceKey, Object... arguments) {
        super(resourceKey);
        this.errorCode = errorCode;
//        this.message = ResourceBundleUtil.getString(resourceKey, arguments);
    }

    @Override
    public String getMessage() {
        return message;
    }

    public int getErrorCode() {
        return errorCode;
    }

}
