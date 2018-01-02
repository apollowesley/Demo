package com.kyl.ps.jee.filter;

import javax.servlet.*;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * Created by Administrator on 2017/2/13 0013.
 */
public class ServerFilter implements Filter{
    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
        System.out.println(".....ServerFilter....");
    }

    public void doFilter(ServletRequest request, ServletResponse response,
                         FilterChain chain) throws IOException, ServletException {
                HttpServletRequest httpServletRequest = (HttpServletRequest) request;
                HttpServletResponse httpServletResponse = (HttpServletResponse) response;
                httpServletResponse.addHeader("Access-Control-Allow-Origin", "*");
                // 当前访问的路径
                final String curURL = httpServletRequest.getRequestURI();
                System.out.println("===你访问过"+""+"得地址==="+curURL);
                chain.doFilter(httpServletRequest, httpServletResponse);
            }

    @Override
    public void destroy() {
    }
}
