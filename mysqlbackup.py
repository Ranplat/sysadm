#!/usr/bin/env python
#_*_ coding:utf-8 _*_
#!/usr/bin/env python
#_*_ coding:utf-8 _*_
#Backup with mysqldump everyday
#Backup Mysql can use on windows or linux
#But TAR Fuction can only use on linux because command different between windows and linux
import time
import datetime
import os
import conf
import smtplib
from email.mime.text import MIMEText

#返回任意一天
class Day(object):
    @staticmethod
    def any_day(add_days):
        today = datetime.date.today()
        utl_add_day = str(today - datetime.timedelta(days=int(add_days)))
        return utl_add_day
    
class MysqlBackup(object):
    def __init__(self,**kargs):
        self.__host = kargs['host']
        self.__dbname = kargs['db']
        self.__username = kargs['user']
        self.__password = kargs['passwd']    
        self.__port = kargs['port']
        
#mysqldump备份数据库        
    def BakData(self,backup_file):
        cmd_bak='mysqldump -u '+self.__username+' -p'+self.__password+' -h'+self.__host +' '+self.__dbname+' --single-transaction '+' > '+backup_file
        outp = os.system(cmd_bak)
        return cmd_bak,outp
    
#Linux下用tar打包压缩备份文件    
    def TarData(self,date):
        cmd_tar='tar zcf '+conf.backup_path+self.__dbname+'_'+date+'.tar.gz '+'-C '+conf.backup_path+' '+self.__dbname+'_'+date+'.dump >> /dev/null 2>&1'
        outp = os.system(cmd_tar)
        return cmd_tar,outp     
       
    @property
    def dbname(self):
        return self.__dbname
    
class sendmail():
    def __init__(self, *args,**kargs):
        self.SMTPserver = kargs['address']
        self.sender = kargs['sender']
        self.password = kargs['password']
        self.destination = args[0]

#登录邮箱发送邮件        
    def send(self,message):
        msg = MIMEText(message,_charset='utf-8') 
        msg['Subject'] = 'Mysql Backup Failed'
        msg['From'] = self.sender
        msg['To'] = self.destination
        mailserver = smtplib.SMTP(self.SMTPserver, 25)
        mailserver.login(self.sender, self.password)
        mailserver.sendmail(self.sender, [self.destination], msg.as_string())
        mailserver.quit()
        print 'send email success'

#主函数起始        
def main():       
    DATA_DATE = Day.any_day(1)
    #发件人和收件人地址
    MAIL_USER_ADDRESS = sendmail(*conf.note_user,**conf.contact_user)
    #初始化需要备份的数据库类
    DB_BAK_INFO = MysqlBackup(**conf.conn_dict)
    backup_file = conf.backup_path+DB_BAK_INFO.dbname+'_'+DATA_DATE+'.dump'
    print backup_file
    log_file = conf.backup_path+DB_BAK_INFO.dbname+'.log'
    #MAIL_USER_ADDRESS.send('I send a message by Python. 你好')
    
    #保存日志
    with open(log_file,'a') as f:
        f.write('\n\n ***********************\n')
        f.write(' * '+time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())+' *\n')
        f.write(' ***********************\n')
        #不存在dump备份文件才备份
        if os.path.isfile(backup_file) is False:
            #备份
            cmd_result = DB_BAK_INFO.BakData(backup_file)
            print cmd_result
            f.write('** COMMAND     :'+cmd_result[0]+'\n')
            f.write('** DATABASE    : '+DB_BAK_INFO.dbname+'\n')
            f.write('** DATA_DATE   : '+DATA_DATE+'\n')
            f.write('** RESULT(BAK) : '+('succeed\n' if cmd_result[1] == 0 else 'failed\n'))
            #备份成功打包
            if cmd_result[1] == 0:
                #打包
                tar_result = DB_BAK_INFO.TarData(DATA_DATE)
                f.write('** COMMAND     :'+tar_result[0]+'\n')
                f.write('** RESULT(TAR) : '+('succeed' if tar_result[1] == 0 else 'failed'))
                #打包成功删除备份文件
                if tar_result[1] == 0:
                    os.remove(backup_file)
                else:
                    MAIL_USER_ADDRESS.send('Mysql备份打包失败，请核查！')
            else:
                MAIL_USER_ADDRESS.send('Mysql数据库备份失败，请核查！')
        else:
            f.write('** RESULT(BAK) : ' +'%s is already exists\n' %backup_file)

#程序入口        
if __name__ == '__main__':
    main()
#bakimeeting.bakData('backup_file')
