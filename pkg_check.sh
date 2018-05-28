#!/usr/bin/bash

release=`uname -a | cut -d' '  -f3`
printf  "kernel version: $release \n"

function checkok() {
    if [ $? -eq 0 ]
    then
        printf "run complete\n"
	return 0
    else
        printf "something error happen\n "
        exit
    fi
}

function pkg_if_exists() {
# check 
com=`command -v $1`

    if [ $? -eq 0  ]
    then
        printf "$1 has be installed\n"
    else
        printf "begin install $1\n"
        yum install -y "$1"  1>/dev/null  
        checkok
    fi
}
 
function network_if_works() {
	printf "check network if available\n"
	ping -c3 baidu.com 1>/dev/null
	if [ $? -eq 0 ]
	then
		printf "net ok... continuw\n"
		return 0
	else
		printf "net works wrong.\n"
		exit 1
	fi
}

network_if_works
pkg_if_exists	net-tools
pkg_if_exists	vim
pkg_if_exists	iptables-services
pkg_if_exists	ntp
