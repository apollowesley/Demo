package com.kyl.ps.util;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

import com.kyl.ps.exception.OutOfRegisterTimeException;

/**
 * 
 * <p>
 * Title: DateUtils
 * </p>
 * <p>
 * Description: com.soarsky.ps.common.util
 * </p>
 * <p>
 * Copyright: Copyright (c) 2013
 * </p>
 * <p>
 * Company: Kyn
 * </p>
 * 
 * @author Jason.Guo
 * @date 2013-3-4
 */
public class DateUtils {

    public final static String  ONLY_DATE_FORMAT       = "yyyy-MM-dd";

    public final static String  DATE_TIME_FORMAT       = "yyyy-MM-dd HH:mm:ss";

    private static final String DATE_PATTERN_IN_DAY    = "yyyy-MM-dd";
    public static final String  DATE_PATTERN_IN_MONTH  = "yyyy-MM";
    private static final String DATE_PATTERN_IN_YEAR   = "yyyy";
    private static final String DATE_PATTERN_IN_SECOND = "yyyy-MM-dd HH:mm:ss";

    // 得到用于数据库查询需要比较的日期时间
    public static String getQueryLastDate(String qDate)
            throws OutOfRegisterTimeException {

        Date qd = java.sql.Date.valueOf(qDate);

        Calendar c = Calendar.getInstance();
        c.setTime(qd);
        c.set(Calendar.DATE, 1);
        c.add(Calendar.MONTH, 1);

        Date lDate = c.getTime();

        return DateUtils.date2StrInDay(lDate);

    }

    /**
     * 处理掉时间所带的天,小时,分,秒
     * 
     * @param dateWithSS
     * @return
     * @throws ParseException
     */
    public static String DateInMonth(String dateWithSS) throws ParseException {
        return date2StrInMonth(str2DateInMonth(dateWithSS));
    }

    /**
     * 处理掉时间所带的小时,分,秒
     * 
     * @param dateWithSS
     * @return
     * @throws ParseException
     */
    public static String DateInDay(String dateWithSS) throws ParseException {
        return date2StrInDay(str2DateInDay(dateWithSS));
    }

    public static int compare_date(String start, String end) {
        DateFormat df = new SimpleDateFormat("yyyy-MM-dd hh:mm");
        try {
            Date dt1 = df.parse(start);
            Date dt2 = df.parse(end);
            if (dt1.getTime() > dt2.getTime()) {

                return 1;
            } else if (dt1.getTime() < dt2.getTime()) {

                return -1;
            } else {
                return 0;
            }
        } catch (Exception exception) {
            exception.printStackTrace();
        }
        return 0;

    }

    /**
     * 获取系统时间,精确到天
     * 
     * @return
     */
    public static String getCurrentDateInDayForTaobao() {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_DAY);
        return sdf.format(new Date()).replaceAll(Constants.DATE_FORMAT_SPLITER,
                "");
    }

    /**
     * 获取系统时间,精确到天
     * 
     * @return
     */
    public static String getCurrentDateInDay() {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_DAY);  
        
        return sdf.format(new Date());
    
    }

    public static String getCurrentDateInMonth() {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_MONTH);
        return sdf.format(new Date());
    }

    /**
     * 获取系统时间,精确到秒
     * 
     * @return
     */
    public static String getCurrentDateInSecond() {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_SECOND);
        return sdf.format(new Date());
    }

    /**
     * 转换日期类型到字符串类型,精确到天
     * 
     * @param date
     * @return
     */
    public static String date2StrInDay(Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_DAY);
        return sdf.format(date);
    }

    public static String date2StrInMonth(Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_MONTH);
        return sdf.format(date);
    }

    public static String date2StrInDayForDB(Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_DAY);
        return date2DBDate(sdf.format(date));
    }

    public static String date2StrInMonthForDB(Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_MONTH);
        return date2DBDate(sdf.format(date));
    }

    public static String date2StrInYearForDB(Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_YEAR);
        return date2DBDate(sdf.format(date));
    }

    public static String date2DBDate(String noDBDate) {
        return noDBDate.replaceAll("-", "_");
    }

    public static String str2StrInDay(String dateStrInSecond)
            throws ParseException {
        return date2StrInDay(str2DateInDay(dateStrInSecond));
    }

    public static String str2StrInDayForDB(String dateStrInSecond)
            throws ParseException {
        return date2DBDate(date2StrInDay(str2DateInDay(dateStrInSecond)));
    }

    public static String str2StrInMonthForDB(String dateStrInSecond)
            throws ParseException {
        return date2DBDate(date2StrInMonthForDB(str2DateInDay(dateStrInSecond)));
    }

    /**
     * 转换日期类型到字符串类型,精确到天
     * 
     * @param date
     * @return
     */
    public static String date2StrInDayForTaobao(Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_DAY);
        return sdf.format(date).replaceAll("-", "");
    }

    /**
     * 转换日期类型到字符串类型,精确到秒
     * 
     * @param date
     * @return
     */
    public static String date2StrInSecond(Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_SECOND);
        return sdf.format(date);
    }

    /**
     * 转换字符串类型到日期类型,精确到天
     * 
     * @param dateStr
     * @return
     * @throws ParseException
     */
    public static Date str2DateInDay(String dateStr) throws ParseException {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_DAY);
        return sdf.parse(dateStr);
    }

    public static Date str2DateInMonth(String dateStr) throws ParseException {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_MONTH);
        return sdf.parse(dateStr);
    }

    /**
     * 转换字符串类型到日期类型,精确到秒
     * 
     * @param dateStr
     * @return
     * @throws ParseException
     */
    public static Date str2DateInSecond(String dateStr) throws ParseException {
        SimpleDateFormat sdf = new SimpleDateFormat(DATE_PATTERN_IN_SECOND);
        return sdf.parse(dateStr);
    }

    /**
     * 
     * <p>
     * Description: 输入一个字符串形式的日期,2010-10-10 10:10,输出以2010-10-10 10:10:00
     * 为时间基点的calendar对象
     * </p>
     * 
     * @param dateStrInMin
     * @return
     * @throws ParseException
     * @author Jason.Guo
     * @date 2013-4-20
     */
    public static Calendar getCalendarByDateInMin(String dateStrInMin)
            throws ParseException {
        Date currentDate = DateUtils.str2DateInSecond(dateStrInMin + ":00");
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(currentDate);
        return calendar;
    }

    public static Date getMonthLastDay(String date) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM");
        Calendar c = Calendar.getInstance();
        try {
            c.setTime(sdf.parse(date));
        } catch (ParseException e) {
            e.printStackTrace();
        }
        // 当前日期
        c.add(Calendar.MONTH, 1);
        int num = c.getActualMaximum(Calendar.DATE);
        c.add(Calendar.DATE, num - 1);
        return c.getTime();
    }

    // 得到用于数据库查询需要比较的日期时间
    public static String getQueryCondMonth() {

        Calendar c = Calendar.getInstance();
        int current = c.get(Calendar.DATE);
        int max = c.getActualMaximum(Calendar.DATE);

        if (current == max)
            c.add(Calendar.MONTH, -1);
        else
            c.add(Calendar.MONTH, -2);

        return DateUtils.date2StrInDay(c.getTime());

    }

    // 得到用于数据库查询需要比较的日期时间
    public static String getQueryCondPerMonth() {

        Calendar c = Calendar.getInstance();
        int current = c.get(Calendar.DATE);
        int max = c.getActualMaximum(Calendar.DATE);

        if (current == max) {
            c.set(Calendar.DATE, 1);
        } else {
            c.add(Calendar.MONTH, -1);
            c.set(Calendar.DATE, 1);
        }

        return DateUtils.date2StrInDay(c.getTime());

    }
    // ----------------

    public static Date getCurrentDate() {
        try {
            return new Date();
        } catch (Exception e) {
            System.out.println(e.getMessage());
            return null;
        }
    }

    public static String getCurrentDate(String patten) throws Exception {
        SimpleDateFormat formatter = new SimpleDateFormat(patten);
        String date = formatter.format(new Date(System.currentTimeMillis()));
        return date;
    }

    public static String getCurrentDateSimpleFormat() throws Exception {
        return getCurrentDate(ONLY_DATE_FORMAT);
    }

    public static String getCurrentDateTimeSimpleFormat() throws Exception {
        return getCurrentDate(DATE_TIME_FORMAT);
    }

    public static long getCurrentTimeStemp() throws Exception {
        return getCurrentDate().getTime();
    }

    public static long getTimeStemp(String dateStr) throws Exception {
        DateFormat format = new SimpleDateFormat(DATE_TIME_FORMAT);
        Date date = format.parse(dateStr);
        return date.getTime();
    }

    public static String getDateTimeString(Date date, String patten)
            throws Exception {
        SimpleDateFormat formatter = new SimpleDateFormat(patten);
        String dateStr = formatter.format(date);
        return dateStr;
    }

    public static String getDateStringTimeSimpleFormat(Date date)
            throws Exception {
        return getDateTimeString(date, DATE_TIME_FORMAT);
    }

    /**
     * 计算时间差(分)
     * 
     * @Description：
     * @author: chengbo
     * @date: 2015年3月26日
     *
     * @param startTime
     * @param endTime
     * @return
     */
    public static long computtTime_minute(Date startTime, Date endTime) {
        long s = 0;
        try {
            long l = endTime.getTime() - startTime.getTime();
            if (l < (1000 * 60)) return 0;
            s = l / (1000 * 60);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return s;
    }

    /**
     * 
     * endDateMoreThanStartDate:(这里用一句话描述这个方法的作用). <br/>
     * 获取2个日期的时间差 天.<br/>
     *
     * @author David.Tang
     * @param startDate
     * @param hours
     * @return
     * @since JDK 1.7
     */

    public static long dateDiff(String startDate,
            String endDate) {
        long secondsInMilli = 1000;
        long minutesInMilli = secondsInMilli * 60;
        long hoursInMilli = minutesInMilli * 60;
        long daysInMilli = hoursInMilli * 24;
        try {
            Date staDate = str2DateInDay(startDate);
            Date eDate = str2DateInDay(endDate);
            long different = eDate.getTime() - staDate.getTime();
            return different/daysInMilli;
        } catch (ParseException e) {
            e.printStackTrace();
        }
        return 0l;
    }
    
    public static long dateDiffBysecond(String startDate,
            String endDate) {
        long secondsInMilli = 1000;
        long minutesInMilli = secondsInMilli * 60;
        long hoursInMilli = minutesInMilli * 60;
        long daysInMilli = hoursInMilli * 24;
        try {
            Date staDate = str2DateInSecond(startDate);
            Date eDate = str2DateInSecond(endDate);
            long different = eDate.getTime() - staDate.getTime();
            return different/daysInMilli;
        } catch (ParseException e) {
            e.printStackTrace();
        }
        return 0l;
    }
    
    public static String getDayBeforeToday(int days){
        SimpleDateFormat formatter = new SimpleDateFormat(ONLY_DATE_FORMAT);
        Calendar calendar = Calendar.getInstance();
        calendar.add(Calendar.DATE, -days);
        return formatter.format(calendar.getTime());
    }
}
