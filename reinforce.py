#!/bin/python2
# -*- coding:utf8 -*-

import re
import os
import sys  
import stat
import fileinput 

def alter(file,old_str,new_str):

    with open(file, "r") as f1,open("%s.bak" % file, "w") as f2:
        for line in f1:
            f2.write(re.sub(old_str,new_str,line))
    os.remove(file)
    os.rename("%s.bak" % file, file)

def chmod_755(list):
    for file in list:
	os.chmod(file,stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
'''
修改ssh配置， 及防火墙允许ssh远程连接
'''
class Alter_ssh(object):
    def __init__(self,ssh_port):
	self._ssh_port = ssh_port
    def alter_iptables_ssh(self):
        with open("/etc/ssh/sshd_config","r") as f:
            file = f.readlines()
            for line in file:
                if len(re.findall(r'Port\s+\d+',line)):
                    origin_port = re.sub('\D','',line)
	patt="--dport\s+"+origin_port
        print patt
        print self._ssh_port
        sub_str="--dport "+str(self._ssh_port)
        alter("/etc/sysconfig/iptables",patt,sub_str)
    def alter_ssh_port(self):
        sub_str="Port "+str(self._ssh_port)
        alter("/etc/ssh/sshd_config", "^(P|#P)ort(\s+\d+)", sub_str)

'''
在指定行前插入
'''
class Insert_line(object):  
  
    def __init__(self, file, keyword, newline):  
        self.__file = file  
        self.__key = keyword  
        self.__newline = newline  
  
    def _get_specify_lineno(self):  
        i = 1  
        try:  
            f = open("%s" % self.__file)  
        except IOError,e:  
            print e[1] + ' "%s"' % e.filename  
            sys.exit(1)  
        while True:  
            line = f.readline()  
            if not line: break  
            if "%s" % self.__key in line:  
                return i  
                break  
            i += 1  
        f.close()  
  
    def _inserted_newline_list(self):  
        if self._get_specify_lineno():  
            ls = os.linesep  
            f = open("%s" % self.__file)  
            li = f.readlines()  
            f.close()  
            li.insert(self._get_specify_lineno() - 1, self.__newline + ls )  
            return li  
  
    def inserted_new_file(self):  
        if self._inserted_newline_list():  
            lines = self._inserted_newline_list()  
            os.system("cp %s %s.bak" % (self.__file, self.__file))  
            f = open("%s" % self.__file, 'w')  
            f.writelines(lines)  
            f.close()  
        else:  
            print 'No such keyword "%s"' % self.__key  

def alter_ssh_port(port):
    file = Alter_ssh(port)
    file.alter_iptables_ssh()
    file.alter_ssh_port()

def alter_selinux_state():
    alter("/etc/selinux/config","SELINUX=\w+","SELINUX=disabled")

def ntpupdate():
    file = Insert_line("/etc/ntp.conf", "server 0", "server time.nist.gov  prefer")  
    file.inserted_new_file()  

def alter_comm_priv():
    list=['/bin/ping','/bin/vim','/bin/tail','/bin/less','/bin/head','/bin/cat','/bin/uname','/bin/ps']
    chmod_755(list)

if __name__ == '__main__':
    alter_ssh_port(22)
    alter_selinux_state()
    ntpupdate()
    alter_comm_priv()
