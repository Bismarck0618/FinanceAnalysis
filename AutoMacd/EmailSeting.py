# encoding=utf-8

"""
    此脚本用于设置发件邮箱的信息，在相应文职设置好信息后，运行该脚本，生成配置文件！
"""
import os

from SDK.AutoEmailSub import dumpPickle

dumpPickle(data=
           "XXXXXXXXX@163.com"                                  # 发件邮箱（需设置）
           + "?"
           + "*******"                                          # 发件邮箱登陆密码（需设置）
           + "?"
           + "['XXXXXXXXXX@qq.com']"                            # 收件邮箱列表（可有多个收件人）（需设置）
           + "?"
           + "smtp.163.com",                                    # 邮件服务器地址（需根据使用的邮箱设置）

           saveLocation=os.path.basename('./Email_Setting'),    # 生成的配置文件保存路径（不用改）
           fileName="senderInfo.txt")                           # 生产的配置文件名称（不用改）