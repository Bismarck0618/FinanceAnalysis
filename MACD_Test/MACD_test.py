# encoding = utf-8

"""
本脚本是用来展示MACD指标的原理过程
"""

import tushare as ts
from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']


# 下载上证指数用来做测试数据
sh_df = ts.get_k_data('sh')

# 增加12日，26日均线
sh_df['M12'] = sh_df.close.rolling(12).mean()
sh_df['M26'] = sh_df.close.rolling(26).mean()
sh_df['M12-M26'] = sh_df['M12'] - sh_df['M26']
sh_df['MM9'] = sh_df['M12-M26'].rolling(9).mean()
sh_df['MM_diff'] = sh_df['M12-M26'] - sh_df['MM9']

sh_df = sh_df.set_index('date',drop=True).dropna(how='any').head(200)

# 画图展示
fig, ax = plt.subplots(nrows=2,ncols=1)
ax[0].plot(sh_df.index, sh_df['close'], 'g--',label='close')
# ax[0].plot(sh_df.index, sh_df['M12'], 'r--',label='12日均线')
# ax[0].plot(sh_df.index, sh_df['M26'], 'b--',label='26日均线')

# ax[1].plot(sh_df.index,sh_df['M12-M26'],'g--',label='12日均线-26日均线')
# ax[1].plot(sh_df.index,sh_df['MM9'],'r--',label='均线后再9日均线')
ax[1].bar(sh_df.index,sh_df['MM_diff'],label='1日均线-9日均线')

ax[0].legend(loc='best')
ax[1].legend(loc='best')
ax[0].set_title('上证收盘价图')
ax[1].set_title('MACD柱型图')
plt.show()
# plt.savefig('./macd.png')


end=0
