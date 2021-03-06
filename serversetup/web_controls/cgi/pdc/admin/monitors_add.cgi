#!/bin/bash
#Copyright (C) 2007  Paul Sharrad

#This file is part of Karoshi Server.
#
#Karoshi Server is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#Karoshi Server is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.
#
#You should have received a copy of the GNU Affero General Public License
#along with Karoshi Server.  If not, see <http://www.gnu.org/licenses/>.

#
#The Karoshi Team can be contacted at: 
#mpsharrad@karoshi.org.uk
#jsharrad@karoshi.org.uk

#
#Website: http://www.karoshi.org.uk
########################
#Required input variables
########################
#  _GROUPNAME_ The name of the mon monitor group to add
#  _TCPIP_  IP numbers of the devices in the group to check
#   _INTERVAL_  The time interval between each check.
#  _DESCRIPTION_
#  _MONITORTYPES_ The type of monitors to use to check the services.
############################
#Language
############################

STYLESHEET=defaultstyle.css
[ -f /opt/karoshi/web_controls/user_prefs/"$REMOTE_USER" ] && source /opt/karoshi/web_controls/user_prefs/"$REMOTE_USER"
export TEXTDOMAIN=karoshi-server

############################
#Show page
############################
echo "Content-type: text/html"
echo ""
echo '<!DOCTYPE html><html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><title>'$"Add Monitors"'</title><meta http-equiv="REFRESH" content="0; URL=monitors_view.cgi"><link rel="stylesheet" href="/css/'"$STYLESHEET"'?d='"$VERSION"'"></head><body><div id="pagecontainer">'
#########################
#Get data input
#########################
DATA=$(cat | tr -cd 'A-Za-z0-9\._:\+-')
#########################
#Assign data to variables
#########################
END_POINT=40
function get_data {
COUNTER=2
DATAENTRY=""
while [[ $COUNTER -le $END_POINT ]]
do
	DATAHEADER=$(echo "$DATA" | cut -s -d'_' -f"$COUNTER")
	if [[ "$DATAHEADER" = "$DATANAME" ]]
	then
		let COUNTER="$COUNTER"+1
		DATAENTRY=$(echo "$DATA" | cut -s -d'_' -f"$COUNTER")
		break
	fi
	let COUNTER=$COUNTER+1
done
}

#Assign GROUPNAME
DATANAME=GROUPNAME
get_data
GROUPNAME="$DATAENTRY"

#Assign TCPIP
DATANAME=TCPIP
get_data
TCPIP="$DATAENTRY"

#Assign INTERVAL
DATANAME=INTERVAL
get_data
INTERVAL="$DATAENTRY"

#Assign ALERTAFTER
DATANAME=ALERTAFTER
get_data
ALERTAFTER="$DATAENTRY"

#Assign DAYSTART
DATANAME=DAYSTART
get_data
DAYSTART="$DATAENTRY"

#Assign DAYEND
DATANAME=DAYEND
get_data
DAYEND="$DATAENTRY"

#Assign HOURSTART
DATANAME=HOURSTART
get_data
HOURSTART="$DATAENTRY"

#Assign HOUREND
DATANAME=HOUREND
get_data
HOUREND="$DATAENTRY"

#Assign MONITORTYPES
COUNTER=2
ARRAY_COUNT=0
while [ "$COUNTER" -le "$END_POINT" ]
do
	DATAHEADER=$(echo "$DATA" | cut -s -d'_' -f"$COUNTER")
	if [[ "$DATAHEADER" = MONITORTYPES ]]
	then
		let COUNTER=$COUNTER+1
		MONITORTYPES["$ARRAY_COUNT"]=$(echo "$DATA" | cut -s -d'_' -f"$COUNTER")
	let ARRAY_COUNT="$ARRAY_COUNT"+1
	fi
	let COUNTER="$COUNTER"+1
done

function show_status {
echo '<SCRIPT language="Javascript">'
echo 'alert("'"$MESSAGE"'")';
echo '</script>'
echo "</div></body></html>"
exit
}
#########################
#Check https access
#########################
if [ https_"$HTTPS" != https_on ]
then
	export MESSAGE=$"You must access this page via https."
	show_status
fi
#########################
#Check user accessing this script
#########################
if [ ! -f /opt/karoshi/web_controls/web_access_admin ] || [ -z "$REMOTE_USER" ]
then
	MESSAGE=$"You must be a Karoshi Management User to complete this action."
	show_status
fi

if [[ $(grep -c ^"$REMOTE_USER": /opt/karoshi/web_controls/web_access_admin) != 1 ]]
then
	MESSAGE=$"You must be a Karoshi Management User to complete this action."
	show_status
fi
#########################
#Check data
#########################
#Check to see that GROUPNAME is not blank
if [ -z "$GROUPNAME" ]
then
	MESSAGE=$"The group name must not be blank."
	show_status
fi

if [ -z "$TCPIP" ]
then
	MESSAGE=$"The TCPIP numbers cannot be blank."
	show_status
fi
#Check to see that MONITORTYPES is not blank
if [ -z "$MONITORTYPES" ]
then
	MESSAGE=$"The monitor type cannot be blank."
	show_status
fi

#Check to see that monitor interval is correct if not blank

if [ ! -z "$HOURSTART" ] || [ ! -z "$HOUREND" ]
then
	#Check that all times are not blank
	if [ -z "$HOURSTART" ] || [ -z "$HOUREND" ]
	then
		MESSAGE=$"You must fill in all of the time interval boxes if you do not want continuous monitoring."
		show_status
	fi
fi
#Convert INTERVAL to numbers
[ -z "$INTERVAL" ] && INTERVAL=5
INTERVAL=$(echo "$INTERVAL" | tr -cd '0-9\._:\n-')
Checksum=$(sha256sum /var/www/cgi-bin_karoshi/admin/monitors_add.cgi | cut -d' ' -f1)
#Add monitor
sudo -H /opt/karoshi/web_controls/exec/monitors_add "$REMOTE_USER:$REMOTE_ADDR:$Checksum:$GROUPNAME:$TCPIP:$ALERTAFTER:$INTERVAL:$DAYSTART:$DAYEND:$HOURSTART:$HOUREND:"`echo ${MONITORTYPES[@]:0} | sed 's/ /:/g'`
EXEC_STATUS="$?"
GROUPNAME=$(echo "$GROUPNAME" | sed 's/+/ /g')
MESSAGE=$(echo "$GROUPNAME: "$"Monitor added.")
if [ "$EXEC_STATUS" = 101 ]
then
	MESSAGE=$"There was a problem adding this monitor. Please check the Karoshi Web administration Logs."
fi
if [ "$EXEC_STATUS" = 102 ]
then
	MESSAGE=$"A monitor group already exists with this name."
fi
if [ "$EXEC_STATUS" = 103 ]
then
	MESSAGE=$"A monitoring server has not been added to the network."
fi
if [ "$EXEC_STATUS" != 0 ]
then
	show_status
fi
exit
