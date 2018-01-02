package com.kyl.ps.thrift;

import org.apache.thrift.TException;

/**
 * Created by Administrator on 2017/2/24 0024.
 */
public class HelloWorldServiceImpl  implements  HelloWorldService.Iface{
    @Override
    public String sayHello(String username) throws TException {
            System.out.println("调用成功:反馈:"+username);
        return "调用成功:反馈:"+username;
    }
}
