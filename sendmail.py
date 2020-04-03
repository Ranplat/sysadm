#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import conf
import smtplib
import os
import email
from email.mime.text import MIMEText
from email.mime.base import MIMEBase


class sendmail():
    def __init__(self, *args, **kargs):
        self.SMTPserver = kargs['address']
        self.sender = kargs['sender']
        self.password = kargs['password']
        self.destination = args[0]

    # # 登录邮箱发送邮件
    # def send(self, message):
    #     msg = MIMEText(message, _charset='utf-8')
    #     msg['Subject'] = 'mail test'
    #     msg['From'] = self.sender
    #     msg['To'] = self.destination
    #     mailserver = smtplib.SMTP_SSL(self.SMTPserver)
    #     mailserver.login(self.sender, self.password)
    #     mailserver.sendmail(self.sender, [self.destination], msg.as_string())
    #     mailserver.quit()
    #     print 'send email success'

    def send(self, message, attachfile):
        msg = email.MIMEMultipart.MIMEMultipart(charset='utf-8')
        msg['Subject'] = "ap_status_statistics"
        msg['From'] = self.sender
        msg['To'] = self.destination
        msg['Date'] = email.utils.formatdate()

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
        print 'send email success'


def main():
    MAIL_USER_ADDRESS = sendmail(*conf.note_user, **conf.contact_user)
    MAIL_USER_ADDRESS.send(message="AP  status",
                           attachfile="network_check.sh")


if __name__ == "__main__":
    main()
