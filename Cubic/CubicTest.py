# encoding = utf-8

from General.GlobalSetting import *
from SDK.SDKHeader import *
import talib
"""
    三次样条拟合测试
"""


import matplotlib.pyplot as plt
import numpy as np


step = 6

sh_index = ts.get_hist_data('cyb')
sh_index['date'] = sh_index.index


# 按时间降序排序，方便计算macd
sh_index = sh_index.sort_values(by='date', ascending=True)

# 在原始df中增加macd信息
sh_index['MACD'], sh_index['MACDsignal'], sh_index['MACDhist'] = talib.MACD(sh_index.close,
                                                                            fastperiod=12, slowperiod=26,
                                                                            signalperiod=9)

sh_index = sh_index.dropna(how='any', axis=0).reset_index(drop=True)
for idx in sh_index.loc[step:, :].index:
    df_part = sh_index.loc[idx-step:idx, ['MACD', 'date']].reset_index(drop=True)

    # 使用2次曲线拟合判断拐点
    c=np.polyfit(np.array(df_part.index), np.array(df_part['MACD']), 2)
    a = c[0]
    b = c[1]
    bottom = -1*(b/(2*a))

    if step-1.5 < bottom < step + 1.5:
        sh_index.loc[idx, 'corner'] = True
    else:
        sh_index.loc[idx, 'corner'] = False


# 画图展示效果
# trick to get the axes
fig, ax = plt.subplots()

df_normal = sh_index[sh_index.corner==False]
x_normal_axis = list(map(lambda x: DateStr2Sec(x), df_normal['date']))
ax.plot(x_normal_axis, df_normal['MACD'],  'g*')

df_corner = sh_index[sh_index.corner==True]
x_corner_axis = list(map(lambda x: DateStr2Sec(x), df_corner['date']))
ax.plot(x_corner_axis, df_corner['MACD'],  'r*')

# plot data
plt.show()

end = 0
