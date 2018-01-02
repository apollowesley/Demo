package com.kyl.ps.model.param;

/**
 * Created by Administrator on 2017/2/6 0006.
 */
public class BaseModel {
    private  String userID;//用户ID
    private  String roleID;//角色ID
    private  String token;//请求唯一标示

    public String getUserID() {
        return userID;
    }

    public void setUserID(String userID) {
        this.userID = userID;
    }

    public String getRoleID() {
        return roleID;
    }

    public void setRoleID(String roleID) {
        this.roleID = roleID;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }
}
