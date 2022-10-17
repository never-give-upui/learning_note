# -*- coding: utf-8 -*-
'''
Copyright (c) 2016-2022, XYAsset. All rights reserved.

Author: YuanLongdi

Create Date: 2022-10-14 16:15:46

Last Time: 2022-10-14 17:40:06

Last Author: YuanLongdi

Description: 
'''
import json
import logging
from check_config import config, check_config
from datetime import datetime
import mail
# with open("./config.json")as json_file:
#    S = json.load(json_file)


def get_now_date():
    now = datetime.now()
    now = datetime(now.year, now.month, now.day)
    return now


def get_tracing_day_list():
    datelist = []
    strl = requests.get("http://218.202.254.2:15380/trading_day/all")
    strl = strl.content
    strl = strl.decode('utf-8')
    strl = json.loads(strl)
    now_year_month = datetime.now()
    now_year_month = datetime(now_year_month.year, now_year_month.month, 1)
    next_year_month = datetime(now_year_month.year, now_year_month.month+1, 1)
    strl = strl["trading_day"]
    for i in strl:
        shift_datetime = datetime.strptime(str(i), '%Y%m%d')
        if (now_year_month <= shift_datetime < next_year_month):
            datelist.append(shift_datetime)
    return datelist
# 从json文件中获取交易日的列表,并转化成当月的交易日标准的时间格式


def get_trace_rules():
    json_laod = json.load("交易规则.json")
    return json_laod


def third_friday(year, month):
    """Return datetime.date for monthly option expiration given year and
    month
    """
    # The 15th is the lowest third day in the month
    third = datetime.date(year, month, 15)
    # What day of the week is the 15th?
    w = third.weekday()
    # Friday is weekday 4
    if w != 4:
        third = third.replace(day=(15 + (4 - w) % 7))
    return third
# 返回YY-MM的第三个周五的日期


def get_tracing_day_num(day):
    num = 0
    list = get_tracing_day_list()
    now = datetime.now()
    month_day = datetime(now.year, now.month, day)
    for i in range(len(list)):
        if (month_day >= list[i]):
            num += 1
    return num
# 每月的x号是第y个交易日


def get_tracing_day_before(day, number):
    list = get_tracing_day_list()
    num = 0
    now = datetime.now()
    month_day = datetime(now.year, now.month, day)
    for i in range(len(list)):
        if (month_day > list[i]):
            num += 1
    return list[num-number]


def check_zs():
    with open("./rules.json", encoding='utf-8') as file:
        rules = json.load(file)
    for i in rules["提醒规则"]["正数交易日"]:
        if (get_now_date() == get_tracing_day_num(i["交易日数"])):
            logging.warning("提醒：当前交易日为本月第{}个交易日，请注意：{}\n", format(
                            i["交易日数"], i["提醒内容"]))
    return 1


def check_ds():
    with open("./rules.json", encoding='utf-8') as file:
        rules = json.load(file)
    mail_list = rules["邮件列表"]
    for i in rules["提醒规则"]["倒数交易日"]:
        if (get_now_date() == get_tracing_day_before(i["起始日(不含)"], i["交易日数"])):
            logging.warning("提醒：当前交易日为本月第{}日前第{}个交易日，请注意：{}\n", format(
                i["起始日(不含)"], i["交易日数"], i["提醒内容"]))
    return 1


def check_day():
    third_fri = third_friday()
    if (get_now_date() == get_tracing_day_before(third_fri, 2)):
        logging.warning("提醒：两天之后股指换合约\n")
    return 1


def set_warning():
    with open("./rules.json", encoding='utf-8') as file:
        rules = json.load(file)
    mail_list = rules["邮件列表"]
    if (check_day() == 1 | check_ds() == 1 | check_zs() == 1):
        for i in mail_list:
            mail.format_addr(i)
            mail.email_notify("Knots交易日历提醒", warning)


if __name__ == '__main__':
    try:
        check_config()
        set_warning()
    except Exception as e:
        logging.warning('warning_trad error: %s', e)
