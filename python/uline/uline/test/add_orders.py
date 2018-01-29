# -*- coding:utf-8 -*-
import traceback


def add_orders():
    try:
        args = 5 / 0
        for pay_way in ['weixin', 'alipay']:
            for i in range(args):
                sql = """insert into orders (channel,appid,mch_id,sub_mch_id,device_info,body,attach,out_trade_no,total_fee,fee_type,
                    spbill_create_ip,auth_code,bank_type,cash_fee_type,cash_fee,settlement_total_fee,coupon_fee,wx_transaction_id,
                    time_end,trade_type,notify_url,notify_count,checked_flag,ul_mch_id,mch_trade_no)
                    values (s%,'wxb68005e5db5d29ce','1900008951','17401342','1000','深圳市优德艺跨境电商','ATTACH订单额外描述','1','10','CNY',
                    '127.0.0.1','123','CFT','CYY','0','0','0','','20161116203549','JSAPI',
                    'http://wxpay.api.cmbxm.mbcloud.com/charges/wxqrscan/notify',1,
                    2,'100000000975',5630146)"""
                self.tdb.execute(sql, (pay_way))
    except Exception as err:
        traceback.print_exc(err)
        print (err)


if __name__ == "__main__":
    add_orders()
