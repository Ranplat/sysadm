#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# Backup with mysqldump everyday
# Backup Mysql can use on windows or linux
# But TAR Fuction can only use on linux because command different between windows and linux
import time
import datetime
import os
import sys
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

    def transmission_binlog_from_rds(self, file):
        try:
            cmd_downfile = 'mysqlbinlog -u '+self.__username+' -p'+self.__password+' -h'+self.__host + ' -P' + \
                str(self.__port) + '  --raw --read-from-remote-server ' + \
                file+' --result-file='+conf.backup_path+''
            print(cmd_downfile)
            outp = os.system(cmd_downfile)
            return cmd_downfile, outp
        except Exception as e:
            print(e)
        else:
            cursor.close()
            self.__conn.close()

    # 增备
    def IncBak(self):
        cursor = self.__conn.cursor()

        # 查看所有binlog日志列表
        sql_binloglast = "show master logs;"
        num = cursor.execute(sql_binloglast)
        self.__conn.commit()
        file_res = cursor.fetchall()

        # 发件人和收件人地址
        MAIL_USER_ADDRESS = sendmail(*conf.note_user, **conf.contact_user)

        # 保存日志
        log_file = conf.backup_path+'bak.log'
        with open(log_file, 'a') as f:
            f.write('\n\n ***********************\n')
            f.write(' * '+time.strftime("%Y-%m-%d %H:%M:%S",
                                        time.localtime())+' *\n')
            f.write(' ***********************\n')
            for i in range(num-1):
                binlog_file = conf.backup_path+file_res[i][0]
                if os.path.isfile(binlog_file) is False:
                    inc_result = self.transmission_binlog_from_rds(
                        file_res[i][0])
                    if inc_result[1] != 0:
                        f.write("{} 增备失败，请核查！\n".format(binlog_file))
                        os.remove(binlog_file)
                        MAIL_USER_ADDRESS.send(message="{} 增备失败".format(binlog_file))
                        exit(1)
                    else:
                        print("binlog {} backup success\n".format(binlog_file))
                        f.write("{} 增备成功！\n".format(binlog_file))


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

# 主函数起始


def main(h=1, m=0):
    while True:
        now = datetime.datetime.now()
        if now.hour == h and now.minute == m:


            # 初始化需要备份的数据库类
            DB_BAK_INFO = MysqlBackup(**conf.conn_dict)

            bak_res = DB_BAK_INFO.IncBak()



        time.sleep(60)


# 程序入口
if __name__ == '__main__':
    main()


'''
配置文件conf.py如下：
#!/usr/bin/env python
# _*_ coding:utf-8 _*_
conn_dict = dict(host='127.0.0.1',user='root',passwd='12345',dbname='08day05',port = 33061)
contact_user = dict(address='smtp.163.com',sender='xxxxxx@163.com',password='xxxxxx')
note_user = ('xxxxxx@126.com',)
backup_path = "D:/KuGou/"
'''
