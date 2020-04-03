#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# Backup with mysqldump everyday
# Backup Mysql can use on windows or linux
# But TAR Fuction can only use on linux because command different between windows and linux
import time
import datetime
import os
import pandas as pd
import pymysql
import conf
import smtplib
from email.mime.text import MIMEText

# 返回任意一天


class Day(object):
    @staticmethod
    def any_day(add_days):
        today = datetime.date.today()
        utl_add_day = str(today - datetime.timedelta(days=int(add_days)))
        return utl_add_day


class MysqlBackup(object):
    def __init__(self, **kargs):
        self.__host = kargs['host']
        self.__dbname = kargs['dbname']
        self.__username = kargs['user']
        self.__password = kargs['passwd']
        self.__port = kargs['port']
        self.__conn = pymysql.connect(host=self.__host, user=self.__username,
                                      password=self.__password, database=self.__dbname, port=self.__port)

    # get table list
    def GetFullTable(self):
        try:
            sql_tablelist = "show tables;"
            table_list = []
            df = pd.read_sql(sql=sql_tablelist, con=self.__conn)
            for i in range(len(df.values)):
                table_list.append(''.join(df.values[i]))
            return table_list

        except Exception as e:
            print(e)
        else:
            self.__conn.close()

    # ignore table
    def GetIgnoreTable(self, ignore_list):
        if type(ignore_list) is list:
            return ignore_list

    # 需要备份的table
    def GetBackupTables(self, full_list, ignore_list):
        backup_list = []
        backup_list = list(set(full_list) ^ set(ignore_list))

        return backup_list

    # 循环dump表

    def BakData(self, backup_list, dump_file):
        try:
            for i in backup_list:
                cmd_bak = 'mysqldump -u'+self.__username+' -p'+self.__password+' -h'+self.__host + ' -B ' + \
                    ' '+self.__dbname + ' -P'+str(self.__port)+' --single-transaction   --set-gtid-purged=off --tables '+i+' --log-error='+conf.backup_path + \
                    ''+'dump.err  '+' >> '+dump_file
                print cmd_bak
                outp = os.system(cmd_bak)
                if outp != 0:
                    exit(1)
            return 0
        except Exception as e:
            print(e)

    def TarData(self, date):
        cmd_tar = 'tar -cf '+conf.backup_path+self.__dbname+'_'+date + \
            '.tar '+' '+conf.backup_path+date+'.dump >> /dev/null 2>&1'
        outp = os.system(cmd_tar)
        return cmd_tar, outp

        @property
        def dbname(self):
            return self.__dbname


class sendmail():
    def __init__(self, *args, **kargs):
        self.SMTPserver = kargs['address']
        self.sender = kargs['sender']
        self.password = kargs['password']
        self.destination = args[0]

    # 登录邮箱发送邮件
    def send(self, message):
        msg = MIMEText(message, _charset='utf-8')
        msg['Subject'] = 'mysql backup fail'
        msg['From'] = self.sender
        msg['To'] = self.destination
        mailserver = smtplib.SMTP_SSL(self.SMTPserver)
        mailserver.login(self.sender, self.password)
        mailserver.sendmail(self.sender, [self.destination], msg.as_string())
        mailserver.quit()
        print 'send email success'


def main(h=21, m=0):
    while True:
        now = datetime.datetime.now()
        if now.hour == h and now.minute == m and now.day % 7 == 0:
            DATA_DATE = str(datetime.date.today())

            # 发件人和收件人地址
            MAIL_USER_ADDRESS = sendmail(*conf.note_user, **conf.contact_user)

            # 初始化需要备份的数据库类
            DB_BAK_INFO = MysqlBackup(**conf.conn_dict)
            dump_file = conf.backup_path+DATA_DATE+'.dump'
            backup_file = conf.backup_path + \
                conf.conn_dict['dbname']+'_'+DATA_DATE+'.tar'
            full_list = DB_BAK_INFO.GetFullTable()
            ignore_list = DB_BAK_INFO.GetIgnoreTable(conf.ignore_tables)
            backup_list = DB_BAK_INFO.GetBackupTables(full_list, ignore_list)

            bak_res = DB_BAK_INFO.BakData(backup_list, dump_file)
            if bak_res == 0:
                # 打包
                tar_result = DB_BAK_INFO.TarData(DATA_DATE)
                if tar_result[1] == 0:
                    os.remove(dump_file)
                else:
                    os.remove(backup_file)
                    MAIL_USER_ADDRESS.send('Mysql备份打包失败，请核查！')
                    print("Mysql备份打包失败，请核查")
            else:
                MAIL_USER_ADDRESS.send('Mysql数据库备份失败，请核查！')
                print("Mysql数据库备份失败，请核查！")

        time.sleep(60)


# 程序入口
if __name__ == '__main__':
    main()


'''
配置文件conf.py如下：
#!/usr/bin/env python
#_*_ coding:utf-8 _*_
conn_dict = dict(host='127.0.0.1',user='root',passwd='12345',dbname='08day05',port = 33061)
contact_user = dict(address='smtp.163.com',sender='xxxxxx@163.com',password='xxxxxx')
note_user = ('xxxxxx@126.com',)
backup_path = "D:/KuGou/"
ignore_tables = ['t_encter_info_history', 't_monitor_ap']
'''
