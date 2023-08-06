#!/bin/sh

MONITORDIR="/var/lib/dhcpd"
#MONITORDIR="dhcpd.leases"

inotifywait -m -e close_write "${MONITORDIR}" | while read NEWFILE
do
	python2.7 /etc/imcautodeploy/verifyNewIMCAndInitializeImcAutoDeploy.py
done
