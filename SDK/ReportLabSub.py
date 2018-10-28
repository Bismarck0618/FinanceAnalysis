# encoding = utf-8
import math
import talib
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.lineplots import LinePlot, Auto
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

from Global.Setting import *
from SDK.AboutTimeSub import convertQuarter2Value, stdMonthDate2ISO, convertValue2Quarter
from SDK.MyTimeOPT import DateStr2Sec, DatetimeStr2Sec, Sec2Datetime


def RPL_Bk_Page(canvas_para,bk_name):
    """
    函数功能：在pdf中增加bk信息，篇幅为一整页，或者更多，以页为单位
    :param bk_name:
    :param days:        用于指示近期的期限，比如近30天
    :return:
    """


    # 插入字符串，用以表明股票代码及名称
    canvas_para.setFont("song", 10)
    if bk_name in ['sh','sz','cyb','sz50','hs300','zxb']:
        stk_name = bk_name

    else:
        stk_name = stk_basic[stk_basic.index==bk_name]['name'].values[0]

    canvas_para.drawString(20, letter[1] - 10, bk_name + stk_name)



    sh_index = ts.get_hist_data(bk_name)
    sh_index['date'] = sh_index.index
    sh_index = sh_index.reset_index(drop=True)


    # 按时间降序排序，方便计算macd
    sh_index = sh_index.sort_values(by='date',ascending=True)

    # 在原始df中增加macd信息
    sh_index['MACD'],sh_index['MACDsignal'],sh_index['MACDhist'] = talib.MACD(sh_index.close,
                                fastperiod=12, slowperiod=26, signalperiod=9)

    # 在原始数据中增加kdj信息
    sh_index['slowk'], sh_index['slowd'] = talib.STOCH(sh_index.high,
                                                       sh_index.low,
                                                       sh_index.close,
                                                       fastk_period=9,
                                                       slowk_period=3,
                                                       slowk_matype=0,
                                                       slowd_period=3,
                                                       slowd_matype=0)


    # 添加rsi信息
    sh_index['RSI5'] = talib.RSI(sh_index.close, timeperiod=5)
    sh_index['RSI12'] = talib.RSI(sh_index.close, timeperiod=12)
    sh_index['RSI30'] = talib.RSI(sh_index.close, timeperiod=30)

    # 添加SAR信息
    sh_index['SAR'] = talib.SAR(
        sh_index.high.values,
        sh_index.low.values,
        acceleration=0.05,
        maximum=0.2)


    # 在原始数据中加入布林线
    sh_index['upper'], sh_index['middle'], sh_index['lower'] = talib.BBANDS(
        sh_index.close,
        timeperiod=20,
        # number of non-biased standard deviations from the mean
        nbdevup=2,
        nbdevdn=2,
        # Moving average type: simple moving average here
        matype=0)


    sh_index = sh_index.dropna(axis=0,how='any')

    close = ExtractPointFromDf_DateX(sh_index, 'date', 'close')
    m5 = ExtractPointFromDf_DateX(sh_index, 'date', 'ma5')
    m10 = ExtractPointFromDf_DateX(sh_index, 'date', 'ma10')
    m20 = ExtractPointFromDf_DateX(sh_index, 'date', 'ma20')

    macd = ExtractPointFromDf_DateX(sh_index, 'date', 'MACD')

    data = [tuple(close),tuple(m10),tuple(m20)]
    data_name = ['close','m10','m20']

    drawing_ave = genLPDrawing(data=data, data_note=data_name,height=letter[1]*0.1)
    renderPDF.draw(drawing=drawing_ave, canvas=canvas_para, x=10, y=letter[1] * 0.85)

    drawing_macd = genBarDrawing(data=macd, data_note=['macd'],height=letter[1]*0.1)
    renderPDF.draw(drawing=drawing_macd, canvas=canvas_para, x=10, y=letter[1]*0.65)


    # 整理kdj信息
    slowk = ExtractPointFromDf_DateX(sh_index, 'date', 'slowk')
    slowd = ExtractPointFromDf_DateX(sh_index, 'date', 'slowd')
    data_kdj = [tuple(slowk),tuple(slowd)]
    data_kdj_note = ['k','d']

    drawing_kdj = genLPDrawing(data=data_kdj, data_note=data_kdj_note,height=letter[1]*0.06)
    renderPDF.draw(drawing=drawing_kdj, canvas=canvas_para, x=10, y=letter[1] * 0.56)

    # 画图RSI信息
    RSI5 = ExtractPointFromDf_DateX(sh_index, 'date', 'RSI5')
    RSI12 = ExtractPointFromDf_DateX(sh_index, 'date', 'RSI12')
    RSI30 = ExtractPointFromDf_DateX(sh_index, 'date', 'RSI30')

    data_RSI = [tuple(RSI5),tuple(RSI12),tuple(RSI30)]
    data_RSI_note = ['RSI5','RSI12','RSI30']

    drawing_RSI = genLPDrawing(data=data_RSI, data_note=data_RSI_note,height=letter[1]*0.1)
    renderPDF.draw(drawing=drawing_RSI, canvas=canvas_para, x=10, y=letter[1] * 0.38)


    # 画图布林线
    upper = ExtractPointFromDf_DateX(sh_index, 'date', 'upper')
    middle = ExtractPointFromDf_DateX(sh_index, 'date', 'middle')
    lower = ExtractPointFromDf_DateX(sh_index, 'date', 'lower')

    data_BOLL = [tuple(upper),tuple(middle),tuple(lower)]
    data_BOLL_note = ['上线','中线','下线']

    drawing_BOLL = genLPDrawing(data=data_BOLL, data_note=data_BOLL_note,height=letter[1]*0.08)
    renderPDF.draw(drawing=drawing_BOLL, canvas=canvas_para, x=10, y=letter[1] * 0.2)

    # 画SAR线
    sar = ExtractPointFromDf_DateX(sh_index, 'date', 'SAR')
    close = ExtractPointFromDf_DateX(sh_index, 'date', 'close')

    data_BOLL = [tuple(sar),tuple(close)]
    data_BOLL_note = ['SAR线','收盘价']


    drawing_BOLL = genLPDrawing(data=data_BOLL, data_note=data_BOLL_note,height=letter[1]*0.08)
    renderPDF.draw(drawing=drawing_BOLL, canvas=canvas_para, x=10, y=letter[1] * 0.05)

    canvas_para.showPage()

    return canvas_para

def ExtractPointFromDf_DateX(df_origin, date_col, y_col, timeAxis='day'):

    """
    函数功能：从一个dataframe中提取两列，组成point列表格式，以供ReportLab画图之用
                同时将日期中的时间提取出来，转为秒。

                本函数主要用来画当日数据！因为将datetime中的date去掉了，只保留time。

    :param df_origin:
    :param x_col:
    :param y_col:
    :return:
    """

    # 将“data”列中的数据解析后，作为新的列增加到df中
    # df_origin = ExtractJsonToColum(df_row=df_origin, col='data')
    # if len(df_origin) == 0:
    #     return []

    # 按时间排序，并删除空值
    df_origin = df_origin.sort_values(by=date_col, ascending=True)
    df_origin = df_origin[True - df_origin[y_col].isnull()]

    # if len(df_origin) == 0:
    #     print('函数 ExtractPointFromDf_DateX：删除空值后，dataframe为空！入参df中不含指定列')
    #     return df_origin

    # 提取时间，并将时间转为秒
    if timeAxis == 'day':
        df_origin['time'] = df_origin.apply(lambda x: DateStr2Sec(str(x[date_col])), axis=1)

    elif timeAxis == 'datetime':
        df_origin['time'] = df_origin.apply(lambda x: DatetimeStr2Sec(str(x[date_col])), axis=1)

    elif timeAxis == 'quarter':
        df_origin['time'] = df_origin.apply(lambda x: convertQuarter2Value(str(x[date_col])), axis=1)

    elif timeAxis == 'year':
        df_origin['time'] = df_origin.apply(lambda x: x[date_col], axis=1)

    elif timeAxis == 'month':
        df_origin['time'] = df_origin.apply(lambda x:DateStr2Sec(stdMonthDate2ISO(str(x[date_col]))),axis=1)

    # 单独取出相应两列，准备转成point格式
    df_part = df_origin.loc[:, ['time', y_col]]

    # 将df转为array
    point_array = list(map(lambda x: (x[0], float(x[1])), df_part.values))

    return point_array

def genLPDrawing(data, data_note, width=letter[0]*0.8, height=letter[1]*0.25, timeAxis='day', y_min_zero=False):
    """
    函数功能：生成Drawing之用
    :return:
    """

    drawing = Drawing(width=width, height=height)

    lp = LinePlot()
    # lp.x = 50
    # lp.y = 50
    lp.height = height
    lp.width = width
    lp.data = data
    lp.joinedLines = 1

    # 定义颜色集
    barFillColors = [
        colors.red, colors.green, colors.blue, colors.darkgoldenrod,
        colors.pink, colors.purple, colors.lightgreen, colors.darkblue, colors.lightyellow,
        colors.fidred, colors.greenyellow, colors.gray, colors.white,colors.blueviolet, colors.lightgoldenrodyellow]

    for i in range(0, len(data)):
        lp.lines[i].name = data_note[i]
        lp.lines[i].symbol = makeMarker('FilledCircle', size=0.5)
        lp.lines[i].strokeWidth = 0.2
        lp.lines[i].strokeColor = barFillColors[i]

    # lp.lineLabelFormat = '%2.0f'
    # lp.strokeColor = colors.black

    x_min = data[0][0][0]
    x_max = data[0][-1][0]

    lp.xValueAxis.valueMin = x_min
    lp.xValueAxis.valueMax = x_max

    if timeAxis=='day':
        step = int(((x_max - x_min) / (60 * 60 * 24)) / 30) + 1

        lp.xValueAxis.valueSteps = [n for n in range(int(x_min), int(x_max), 60 * 60 * 24 * step)]
        lp.xValueAxis.labelTextFormat = lambda x: str(Sec2Datetime(x)[0:10])
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.labels.fontSize = 6
        lp.xValueAxis.labels.dy = -18
        if y_min_zero:
            lp.yValueAxis.valueMin = 0

        # lp.yValueAxis.valueMax = 50
        # lp.yValueAxis.valueSteps = [1, 2, 3, 5, 6]

    elif timeAxis=='quarter':

        step = int(((x_max - x_min)/0.25) / 30) + 1

        lp.xValueAxis.valueSteps = [n for n in range(int(x_min), int(x_max), int(math.ceil(0.25 * step)))]
        lp.xValueAxis.labelTextFormat = lambda x: convertValue2Quarter(x)
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.labels.fontSize = 6
        lp.xValueAxis.labels.dy = -18

        if y_min_zero:
            lp.yValueAxis.valueMin = 0

    elif timeAxis=='year':

        lp.xValueAxis.valueSteps = [n for n in range(int(x_min), int(x_max), 1)]
        lp.xValueAxis.labelTextFormat = lambda x: str(x)
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.labels.fontSize = 6
        lp.xValueAxis.labels.dy = -18

        if y_min_zero:
            lp.yValueAxis.valueMin = 0

    elif timeAxis=='month':

        lp.xValueAxis.valueSteps = list(map(lambda x:x[0],data[0]))
        lp.xValueAxis.labelTextFormat = lambda x: str(Sec2Datetime(x))[0:7]
        lp.xValueAxis.labels.angle = 90
        lp.xValueAxis.labels.fontSize = 6
        lp.xValueAxis.labels.dy = -18

        if y_min_zero:
            lp.yValueAxis.valueMin = 0

    drawing.add(lp)
    add_legend(draw_obj=drawing, chart=lp, pos_x=10, pos_y=-20)

    return drawing

def genBarDrawing(data, data_note, width=letter[0]*0.8, height=letter[1]*0.25):
    """
    函数功能：生成Drawing之用
    :return:
    """
    data_value = list(map(lambda x:x[1],data))

    data_finale = [tuple(data_value)]

    drawing = Drawing(width=width, height=height)


    bc = VerticalBarChart()

    # bc.x = 50
    # bc.y = 50
    # bc.height = 125
    bc.width = width
    bc.data = data_finale
    # bc.valueAxis.valueMin = 0
    bc.barSpacing = 0

    # bc.valueAxis.valueMax = 50
    # bc.valueAxis.valueStep = 10
    # bc.categoryAxis.style = 'stacked'
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30

    barFillColors = [
        colors.red, colors.green, colors.white, colors.blue, colors.yellow,
        colors.pink, colors.purple, colors.lightgreen, colors.darkblue, colors.lightyellow,
        colors.fidred, colors.greenyellow, colors.gray, colors.blueviolet, colors.lightgoldenrodyellow]

    for i in range(len(data_finale)):
        bc.bars[i].name = data_note[i]

        # 最多只支持15种颜色，多出的设置为红色
        if i < 15:
            bc.bars[i].fillColor = barFillColors[i]
        else:
            bc.bars[i].fillColor = colors.red

    # x_min = data[0][0]
    # x_max = data[-1][0]

    # bc.xValueAxis.valueMin = x_min
    # lp.xValueAxis.valueMax = x_max

    # step = int(((x_max - x_min) / (60 * 60 * 24)) / 15) + 1

    # bc.categoryAxis.categoryNames = [str(Sec2Datetime(x))[0:10] for x in range(int(x_min), int(x_max), 60 * 60 * 24 * step)]

    drawing.add(bc)

    # 增加legend
    # add_legend(drawing, bc, pos_x=10, pos_y=-10)

    return drawing

def add_legend(draw_obj, chart, pos_x, pos_y):

    """
    函数功能：voltGroupDisplayByBar函数的子函数
    :param draw_obj:
    :param chart:
    :return:
    """
    legend = Legend()
    legend.alignment = 'right'
    legend.fontName = 'song'
    legend.columnMaximum = 2
    legend.x = pos_x
    legend.y = pos_y
    legend.colorNamePairs = Auto(obj=chart)
    draw_obj.add(legend)
