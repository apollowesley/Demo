/**
 * Created by xiezhigang on 16/12/05.
 * highcharts时间显示错误
 * 如果x轴和数据的时间是用date对象的UTC方法产生的，需要注意这个方法获取的月份参数应该比实际月份少一。。。
 * 因为date对象里一月份对应的是0，二月份对应的是1。因此如果数据原始时间格式是%Y-%m-%d的话，不推荐用UTC方法。
 * 而用上面写到的parse方法的话，在中国会存在时间错位8小时的问题，因为parse是根据当前时区（东8）的时间生成的timestamp，
 * 而highcharts是用标准时来解析的。解决方法是给highcharts一个全局变量指定时区偏移8小时，或者关闭UTC设置。
 */
$(document).ready(function () {
    $("ul.tabs li:first").addClass("active").show();
    $(".tab_content:first").show();

    if($('input[name="query_date"]').val()==2){
        var showTime=24 * 3600 * 1000 * 30;
        var showTimeType= '{value:%Y-%m}';
    }else{
        var showTime=24 * 3600 * 1000;
        var showTimeType= '{value:%Y-%m-%d}';
    }

    $('#highCharts1').highcharts({
        title: {
            text: ''
        },
        exporting: {
            enabled:false
        },
        credits: {
          enabled:false
        },
        xAxis: {
            type: 'datetime',
            labels: {
                format: showTimeType
            }
        },
        yAxis: {
            decimal: true,
            title: {
                text: ''
            },
            labels: {
                formatter: function () {
                    return this.value;
                }
            }
        },
        series: [{
            type: 'area',
            name: '支付成功笔数',
            pointStart: Date.parse(create_start_at),
            pointInterval: showTime,
            data: tx_count_chart
        }],
        tooltip: {
            pointFormat: '{series.name} <b>{point.y}</b><br/>'
        }
    });
    $("ul.tabs li").click(function () {
        $("ul.tabs li").removeClass("active");
        $(this).addClass("active");
        var activeTab = $(this).find("a").attr("href");
        $(activeTab).fadeIn();
        var chart_data = "";
        var chart_name = $(this).find('h4').text();
        if (activeTab == "#tab1") {
            chart_data = tx_count_chart;
        } else if (activeTab == "#tab2") {
            chart_data = tx_amount_chart;
        } else if (activeTab == "#tab3") {
            chart_data = refund_count_chart;
        } else if (activeTab == "#tab4") {
            chart_data = refund_amount_chart;
        } else if (activeTab == "#tab5") {
            chart_data = tx_net_amout_chart;
        } else if (activeTab == "#tab6") {
            chart_data = profit_amount_chart;
        }
        $('#highCharts1').highcharts({
            title: {
                text: ''
            },
            exporting: {
                enabled:false
            },
            credits: {
                enabled:false
            },
            xAxis: {
                type: 'datetime',
                labels: {
                    format: showTimeType
                }
            },
            yAxis: {
                decimal: true,
                title: {
                    text: ''
                },
                labels: {
                    formatter: function () {
                        return this.value;
                    }
                }
            },
            series: [{
                type: 'area',
                name: chart_name,
                pointStart: Date.parse(create_start_at),
                pointInterval: showTime,
                data: chart_data
            }],
            tooltip: {
                pointFormat: '{series.name} <b>{point.y}</b><br/>'
            }
        });
        return false;
    });

});