#!/bin/bash

/sbin/service iptables status 1>/dev/null 2>&1
if [ $? -nt 0 ]; then
        # ipatbles is started
        systemctl  start iptables
        echo "iptables started..."
else
        systemctl  restart   iptables
	echo "iptables restarted..."
fi

f_ntp=`ps aux | grep ntp | grep -v grep | wc -l`
if [ $f_ntp -gt 0 ]; then
        # ntpd is started
        systemctl  restart ntpd
        echo "ntp restarted..."
else
        systemctl  start   ntpd
        echo "sshd  started..."
fi

f_ssh=`ps aux | grep ssh | grep -v grep | wc -l`
if [ $f_ssh -gt 0 ]; then
        # sshd is started
        systemctl  restart sshd
        echo "ssh restarted..."
else
        systemctl  start   sshd
        echo "sshd  started..."
fi
