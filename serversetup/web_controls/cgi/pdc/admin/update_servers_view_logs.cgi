#!/bin/bash
#Copyright (C) 2012  Paul Sharrad

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
#  _LOGVIEW_
#  _DAY_
#  _MONTH_
#  _YEAR_
#  _DAY2_
#  _MONTH2_
#  _YEAR2_

#Detect mobile browser
MOBILE=no
source /opt/karoshi/web_controls/detect_mobile_browser
source /opt/karoshi/web_controls/version

############################
#Language
############################

STYLESHEET=defaultstyle.css
TIMEOUT=300
NOTIMEOUT=127.0.0.1
[ -f /opt/karoshi/web_controls/user_prefs/"$REMOTE_USER" ] && source /opt/karoshi/web_controls/user_prefs/"$REMOTE_USER"
export TEXTDOMAIN=karoshi-server

#Check if timout should be disabled
if [[ $(echo "$REMOTE_ADDR" | grep -c "$NOTIMEOUT") = 1 ]]
then
	TIMEOUT=86400
fi

echo "Content-type: text/html"
echo ""
echo '<!DOCTYPE html><html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><title>'$"View Server Update Logs"'</title><meta http-equiv="REFRESH" content="'$TIMEOUT'; URL=/cgi-bin/admin/logout.cgi"><meta name="viewport" content="width=device-width, initial-scale=1"> <!--480-->'
echo "<link rel=\"stylesheet\" href=\"/css/$STYLESHEET\"><script src=\"/all/stuHover.js\" type=\"text/javascript\"></script>"

if [ "$MOBILE" = yes ]
then
	echo '<link rel="stylesheet" type="text/css" href="/all/mobile_menu/sdmenu.css">
	<script src="/all/mobile_menu/sdmenu.js">
		/***********************************************
		* Slashdot Menu script- By DimX
		* Submitted to Dynamic Drive DHTML code library: www.dynamicdrive.com
		* Visit Dynamic Drive at www.dynamicdrive.com for full source code
		***********************************************/
	</script>
	<script>
	// <![CDATA[
	var myMenu;
	window.onload = function() {
		myMenu = new SDMenu("my_menu");
		myMenu.init();
	};
	// ]]>
	</script>'
fi


echo '</head><body><div id="pagecontainer">'
#########################
#Get data input
#########################
DATA=$(cat | tr -cd 'A-Za-z0-9\._:\-')
#########################
#Assign data to variables
#########################
END_POINT=19
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

#Assign LOGVIEW
DATANAME=LOGVIEW
get_data
LOGVIEW="$DATAENTRY"

#Assign DATE
DATANAME=DATE
get_data
DATE=$(echo "$DATAENTRY" | tr -cd '0-9-')

#Assign SERVERNAME
DATANAME=SERVERNAME
get_data
SERVERNAME="$DATAENTRY"

#Assign SERVERTYPE
DATANAME=SERVERTYPE
get_data
SERVERTYPE="$DATAENTRY"

#Assign SERVERMASTER
DATANAME=SERVERMASTER
get_data
SERVERMASTER="$DATAENTRY"

function show_status {
echo '<SCRIPT language="Javascript">'
echo 'alert("'"$MESSAGE"'")';
echo '                window.location = "/cgi-bin/admin/update_servers_view_logs_fm.cgi";'
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

if [[ $(grep -c ^"$REMOTE_USER:" /opt/karoshi/web_controls/web_access_admin) != 1 ]]
then
	MESSAGE=$"You must be a Karoshi Management User to complete this action."
	show_status
fi
#########################
#Check data
#########################
#Check to see that LOGVIEW is not blank
if [ -z "$LOGVIEW" ]
then
	MESSAGE=$"The log view must not be blank."
	show_status
fi
#Check to see that DATE is not blank
if [ -z "$DATE" ]
then
	MESSAGE=$"The date must not be blank."
	show_status
fi

#Check that date is valid
DAY=$(echo "$DATE" | cut -d- -f1)
MONTH=$(echo "$DATE" | cut -d- -f2)
YEAR=$(echo "$DATE" | cut -d- -f3)

if [ -z "$DAY" ]
then
	MESSAGE=$"Incorrect date format."
	show_status
fi

if [ -z "$MONTH" ]
then
	MESSAGE=$"Incorrect date format."
	show_status
fi

if [ -z "$YEAR" ]
then
	MESSAGE=$"Incorrect date format."
	show_status
fi

if [ "$DAY" -gt 31 ]
then
	MESSAGE=$"Incorrect date format."
	show_status
fi

if [ "$MONTH" -gt 12 ]
then
	MESSAGE=$"Incorrect date format."
	show_status
fi

if [ "$YEAR" -lt 2006 ] || [ "$YEAR" -gt 3006 ]
then
	MESSAGE=$"Incorrect date format."
	show_status
fi

#Generate navigation bar
if [ "$MOBILE" = no ]
then
	DIV_ID=actionbox3
	#Generate navigation bar
	/opt/karoshi/web_controls/generate_navbar_admin
else
	DIV_ID=mobileactionbox
fi

Checksum=$(sha256sum /var/www/cgi-bin_karoshi/admin/update_servers_view_logs.cgi | cut -d' ' -f1)
#Show logs


#Show back button for mobiles
if [ "$MOBILE" = yes ]
then
	echo '<div style="float: center" id="my_menu" class="sdmenu">
	<div class="expanded">
	<span>'$"View Server Update Logs"'</span>
<a href="/cgi-bin/admin/mobile_menu.cgi">'$"Menu"'</a>
</div></div><div id="mobilecontent"><div id="mobileactionbox2">
'
else
	WIDTH=100
	ICON1=/images/submenus/system/computer.png

	echo '
	<div id="'"$DIV_ID"'"><div id="titlebox">
	<div class="sectiontitle">'$"View Server Update Logs"' <a class="info" target="_blank" href="http://www.linuxschools.com/karoshi/documentation/wiki/index.php?title=Update_Servers#Viewing_Update_Logs"><img class="images" alt="" src="/images/help/info.png"><span>'$"Choose the date that you want to view the update logs for."'</span></a></div>
	<table class="tablesorter"><tbody><tr>

		<td style="vertical-align: top; height: 30px; white-space: nowrap; min-width: '$WIDTH'px; text-align:center;">
			<form name="myform" action="update_servers_view_logs_fm.cgi" method="post">
				<button class="info infonavbutton" name="SelectServer" value="_">
					<img src="'$ICON1'" alt="'$"Select server"'">
					<span>'$"Select a server to view the logs on."'</span><br>
					'$"Select server"'
				</button>
			</form>
		</td>

	</tr></tbody></table></div><div id="infobox">
	'
fi

sudo -H /opt/karoshi/web_controls/exec/update_servers_view_logs "$REMOTE_USER:$REMOTE_ADDR:$Checksum:$LOGVIEW:$DAY:$MONTH:$YEAR:$SERVERNAME:$SERVERTYPE:$SERVERMASTER:$MOBILE:"
LOG_STATUS="$?"
echo '</div>'
if [ "$LOG_STATUS" = 101 ]
then
	MESSAGE=$"There is no log available for this date."
	show_status
fi
if [ "$LOG_STATUS" = 102 ]
then
	MESSAGE=$"There are no logs available for this month."
	show_status
fi
echo '</div></div></body></html>'
exit
