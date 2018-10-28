# encoding = utf-8

"""
这个脚本用来每天定时检测相关股票的macd指标是否处于拐点区域，若处于拐点，则将其打印到pdf中，并发送邮件
"""
import os

import talib
import tushare as ts
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from SDK.AutoEmailSub import sendMail
from SDK.MyTimeOPT import get_current_date_str



# 定义我的关注的股票
from SDK.ReportLabSub import RPL_Bk_Page

# 将你每日需要检查的股票写入下面ARRAY中
# 上证、深成、创业板、中小板 分别用 sh sz cyb zxb 代表

my_focus = [
            '000333',
            '300508']


def macd_test_daily():

    step = 5
    datenow = get_current_date_str()

    # 创建pdf
    c = canvas.Canvas('./MACD_PDF/'+U"MACD检测" + datenow + ".pdf", pagesize=letter)

    # 是否存在相应合适的
    exist_flag = False

    stk_code = my_focus

    # 检测几个大盘指数
    for bk in ['sh','sz','cyb'] + stk_code:

        # 下载数据
        df_bk = ts.get_k_data(bk)

        if df_bk.empty:
            print('函数 macd_test_daily：stk ' + bk +'没有数据！')
            continue

        # 只取时间上最新的100条数据
        df_bk = df_bk.loc[len(df_bk)-150:,:]

        # 为数据添加MACD指标
        df_bk['MACD'], df_bk['MACDsignal'], df_bk['MACDhist'] = talib.MACD(df_bk.close,
                                                                            fastperiod=12, slowperiod=26,
                                                                            signalperiod=9)

        # 获取最后step个数据
        df_last = df_bk.loc[(len(df_bk)-step):,['MACD']].reset_index()

        # 使用2次曲线拟合判断拐点
        coe=np.polyfit(np.array(df_last.index), np.array(df_last['MACD']), 2)
        a = coe[0]
        b = coe[1]
        bottom = -1*(b/(2*a))

        if step-1.5 < bottom < step + 1.5:
            c = RPL_Bk_Page(c, bk)
            exist_flag = True

        print('完成stk' + bk + '的MACD检测！')

    # 如果存在macd指标符合的股票，生成pdf并发送邮件
    if exist_flag:
        c.save()

        # 发送邮件
        sendMail("MACD日度检测" + datenow,
                 [],
                 '',
                 './MACD_PDF/'+U"MACD检测" + datenow + ".pdf")

    else:
        # 发送邮件
        sendMail("MACD检测" + datenow,
                 [],
                 'Nothing happened today!')

# -------------------------- 测试 --------------------------------
# macd_test_daily()

