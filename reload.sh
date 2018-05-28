#!/bin/bash

f_iptables=`ps aux | grep iptables | grep -v grep | wc -l`
if [ $f_iptables -gt 0 ]; then
        # ipatbles is started
        systemctl  restart iptables
        echo "iptables restarted..."
else
        systemctl  start   iptables
	echo "iptables started..."
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
