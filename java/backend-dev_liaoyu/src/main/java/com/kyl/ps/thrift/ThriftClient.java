package com.kyl.ps.thrift;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

/**
 * Created by Administrator on 2017/2/24 0024.
 */
public class ThriftClient {
    public static final String SERVER_IP = "localhost";
    public static final int SERVER_PORT = 8090;
    public static final int TIMEOUT = 30000;
    public void sendData(String data){
        TTransport transport = null;
        try
        {
            transport = new TSocket(SERVER_IP, SERVER_PORT, TIMEOUT);
            // 协议要和服务端一致
            TProtocol protocol = new TBinaryProtocol(transport);
            // TProtocol protocol = new TCompactProtocol(transport);
            // TProtocol protocol = new TJSONProtocol(transport);
            HelloWorldService.Client client = new HelloWorldService.Client(protocol);
            transport.open();
            String result = client.sayHello(data);
            System.out.println("Thrify client result =: " + result);
        } catch (TTransportException e) {
            e.printStackTrace();
        } catch (TException e) {
            e.printStackTrace();
        } finally {
            if (null != transport) {
                transport.close();
            }
        }
    }
    /**
     * @param args
     */
    public static void main(String[] args) {
        ThriftClient client = new ThriftClient();
        client.sendData("china");

    }
}