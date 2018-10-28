# enconding = utf-8

import time
from apscheduler.schedulers.blocking import BlockingScheduler

from AutoMacd.MACD_Check import macd_test_daily

# 创建定时器
sched = BlockingScheduler()
sched.add_job(func=macd_test_daily, trigger='cron', day_of_week='mon-sat', hour=5, minute=0)

sched.start()