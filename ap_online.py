#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import pymysql
import pandas as pd
import time
import datetime
import xlwt
import openpyxl
import conf
import smtplib
import os
import email
from email.mime.text import MIMEText
from email.mime.base import MIMEBase


__author__ = "cai"

# db params
host = "47.103.34.233"
port = 13306
database = "cloudap31"
username = "data"
password = "123@abcd"

# query params
start_time = "2020-03-30"
stop_time = "2020-04-02"


def conn():
    connect = pymysql.connect(host=host, user=username,
                              password=password, database=database, port=port)
    return connect


def getTimeDiff(timeStra, timeStrb):
    if timeStra <= timeStrb:
        return 0
    ta = time.strptime(timeStra, "%Y-%m-%d %H:%M:%S")
    tb = time.strptime(timeStrb, "%Y-%m-%d %H:%M:%S")
    y, m, d, H, M, S = ta[0:6]
    dataTimea = datetime.datetime(y, m, d, H, M, S)
    y, m, d, H, M, S = tb[0:6]
    dataTimeb = datetime.datetime(y, m, d, H, M, S)
    secondsDiff = (dataTimea-dataTimeb).seconds
    daysDiff = (dataTimea-dataTimeb).days
    minutesDiff = daysDiff*1440+round(secondsDiff/60, 1)
    return minutesDiff
    # hoursDiff = daysDiff*24+round(secondsDiff/3600, 1)
    # return hoursDiff


def getMacList():
    get_mac_list_sql = "select distinct mac from t_ap_log where  time > '{}'  and  time < '{}' ".format(
        start_time, date_time(stop_time=stop_time))
    df = pd.read_sql(sql=get_mac_list_sql, con=conn)
    mac_list = df.values
    return mac_list


def date_time(stop_time, interval_days=1):

    date = str(datetime.datetime.strptime(stop_time, "%Y-%m-%d") +
               datetime.timedelta(days=int(interval_days)))
    return date


class sendmail():
    def __init__(self, *args, **kargs):
        self.SMTPserver = kargs['address']
        self.sender = kargs['sender']
        self.password = kargs['password']
        self.destination = args[0]

    # 登录邮箱发送邮件
    def send(self, message, attachfile):
        msg = email.MIMEMultipart.MIMEMultipart(
            message=message, charset='utf-8')
        msg['Subject'] = "ap_status_statistics({}-{})".format(
            start_time, stop_time)
        msg['From'] = self.sender
        msg['To'] = self.destination

        # 构造MIMEText对象做为邮件显示内容并附加到根容器
        text = email.MIMEText.MIMEText(message)
        msg.attach(text)

        # 构造MIMEBase对象做为文件附件内容并附加到根容器
        contype = 'application/octet-stream'
        maintype, subtype = contype.split('/', 1)

        # 读入文件内容并格式化
        data = open(attachfile, 'rb')
        file_msg = MIMEBase(maintype, subtype)
        file_msg.set_payload(data.read())
        data.close()
        email.encoders.encode_base64(file_msg)

        # 设置附件头
        basename = os.path.basename(attachfile)
        file_msg.add_header('Content-Disposition',
                            'attachment', filename=basename)
        msg.attach(file_msg)

        mailserver = smtplib.SMTP_SSL(self.SMTPserver)
        mailserver.login(self.sender, self.password)
        mailserver.sendmail(self.sender, [self.destination], msg.as_string())
        mailserver.quit()


if __name__ == '__main__':

    try:
        conn = conn()

        time_list = []
        owner_list = []
        ap_list = []
        restart_list = []
        mac_list = getMacList()

        for i in range(len(mac_list)):
            status_time_list = []
            online_time = 0

            get_status_sql = "select status,time from t_ap_log where   mac = '{}'   and time > '{}'  and  time < '{}' group by time".format(
                "".join(mac_list[i]), start_time, date_time(stop_time=stop_time))
            df = pd.read_sql(sql=get_status_sql, con=conn)
            for j in range(len(df.values)):
                status_time_list.append(df.values[j][0])
                status_time_list.append(df.values[j][1])

            get_max_time_status_sql = "select status,time,mac from t_ap_log where   mac = '{}'   and time > '{}'  and  time < '{}' group by time  desc limit 1 ".format(
                "".join(mac_list[i]), start_time, date_time(stop_time=stop_time))
            df = pd.read_sql(sql=get_max_time_status_sql, con=conn)
            if df.values[0][0] == '1':
                max_time_status_0 = date_time(stop_time=stop_time)
                status_time_list.extend(['0', max_time_status_0])

            get_min_time_status_sql = "select t_ap_log.status,t_ap_log.time,t_ap_log.mac,t_ap_info.owner from t_ap_log LEFT JOIN t_ap_info ON ( t_ap_log.mac = t_ap_info.mac ) where   t_ap_log.mac = '{}'   and t_ap_log.time > '{}'  and  t_ap_log.time < '{}' group by t_ap_log.time   limit 1 ".format(
                "".join(mac_list[i]), start_time, date_time(stop_time=stop_time))
            df = pd.read_sql(sql=get_min_time_status_sql, con=conn)
            if df.values[0][0] == '0':
                min_time_status_1 = start_time + ' 00:00:00'
                status_time_list.insert(0, '1')
                status_time_list.insert(1, min_time_status_1)

            # print status_time_list
            for k in range(len(status_time_list)/4):
                online_time += float(getTimeDiff(
                    status_time_list[k*4+3], status_time_list[k*4+1]))
            # print status_time_list, online_time, df.values[0][2]

            time_list.append(round(online_time/60, 1))
            ap_list.append(str(df.values[0][2]))
            owner_list.append(str(df.values[0][3]))
            restart_list.append((len(status_time_list)-4)/4)

        data = {

            '日期': start_time+'-'+stop_time,

            'MAC地址': ap_list,

            '用户': owner_list,

            'AP在线时长': time_list,

            '重启次数': restart_list

        }

        df = pd.DataFrame(data)
        excel = "ap_status_statistics({}-{}).xlsx".format(start_time,
                                                          stop_time)

        df.to_excel(excel_writer=excel,
                    sheet_name=start_time+'-'+stop_time)

        MAIL_USER_ADDRESS = sendmail(*conf.note_user, **conf.contact_user)
        MAIL_USER_ADDRESS.send(
            message="AP status statistics", attachfile=excel)

    except Exception as e:
        print(e)

'''
#!/usr/bin/env python
# _*_ coding:utf-8 _*_

contact_user = dict(address='smtp.exmail.qq.com',sender='report@sdnware.com',password='TanWei123')
note_user = ('caishuijin@sdnware.com',)
'''
