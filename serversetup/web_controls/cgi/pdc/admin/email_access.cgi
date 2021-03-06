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

#Detect mobile browser
MOBILE=no
source /opt/karoshi/web_controls/detect_mobile_browser
source /opt/karoshi/web_controls/version

##########################
#Language
##########################

STYLESHEET=defaultstyle.css
[ -f /opt/karoshi/web_controls/user_prefs/"$REMOTE_USER" ] && source /opt/karoshi/web_controls/user_prefs/"$REMOTE_USER"
export TEXTDOMAIN=karoshi-server

##########################
#Show page
##########################
echo "Content-type: text/html"
echo ""
echo '<!DOCTYPE html><html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><title>'$"E-Mail Access"'</title><link rel="stylesheet" href="/css/'"$STYLESHEET"'?d='"$VERSION"'">
<script src="/all/js/jquery.js"></script>
<script src="/all/js/script.js"></script>
<script src="/all/js/jquery.tablesorter/jquery.tablesorter.js"></script>
<script id="js">
$(document).ready(function() 
    { 
        $("#myTable").tablesorter(); 
    } 
);
</script>
<meta name="viewport" content="width=device-width, initial-scale=1"> <!--480-->'

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
echo '</head><body onLoad="start()"><div id="pagecontainer">'

#########################
#Get data input
#########################
DATA=$(cat | tr -cd 'A-Za-z0-9\._:\-')
#echo $DATA"<br>"
#########################
#Assign data to variables
#########################
END_POINT=15
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

#Assign USERSELECT
DATANAME=USERSELECT
get_data
USERSELECT="$DATAENTRY"

#Assign ACTION
DATANAME=ACTION
get_data
ACTION="$DATAENTRY"

#Assign ACCESSLEVEL
DATANAME=ACCESSLEVEL
get_data
ACCESSLEVEL="$DATAENTRY"

#Assign GROUP
DATANAME=GROUP
get_data
GROUP="$DATAENTRY"

#Generate navigation bar
if [ $MOBILE = no ]
then
	DIV_ID=actionbox3
	#Generate navigation bar
	/opt/karoshi/web_controls/generate_navbar_admin
else
	DIV_ID=actionbox2
fi

function show_status {
echo '<script>'
echo 'alert("'"$MESSAGE"'");'
echo 'window.location = "/cgi-bin/admin/email_access.cgi";'
echo '</script>'
echo "</div></div></body></html>"
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

#Check that action is not blank
if [ -z "$ACTION" ]
then
	ACTION=getchoice
fi

if [ "$ACTION" = view ]
then
	if [ -z "$USERSELECT" ]
	then
		ACTION=getchoice
	fi
	#Check to see if the user or the group exists
	getent group "$USERSELECT" 1>/dev/null
	if [ "$?" != 0 ]
	then
		getent passwd "$USERSELECT" 1>/dev/null
		if [ "$?" != 0 ]
		then
			MESSAGE=$"The username or group you have chosen does not exist."
			show_status
		fi
	fi
fi

#Show back button for mobiles
if [ "$MOBILE" = yes ]
then
	echo '<div style="float: center" id="my_menu" class="sdmenu">
	<div class="expanded">
	<span>'$"E-Mail Access"'</span>
<a href="/cgi-bin/admin/mobile_menu.cgi">'$"Menu"'</a>
</div></div><div id="mobileactionbox">'
	if [ "$ACTION" != viewrestrictionlist ]
	then
		echo '<form action="/cgi-bin/admin/email_access.cgi" method="post"><input name="_ACTION_viewrestrictionlist_" type="submit" class="button" value="'$"View Restriction List"'"></form>'
	fi
	if [ "$ACTION" != getchoice ]
	then
		echo '<a href="email_access.cgi"><input class="button" type="button" name="" value="'$"Choose User / group"'"></a>'
	fi
	echo '<br><br>'
else

	WIDTH=100
	ICON1=/images/submenus/system/edit.png
	ICON2=/images/submenus/user/users.png

	echo '<div id="'"$DIV_ID"'"><div id="titlebox">


	<div class="sectiontitle">'$"E-Mail Access"' <a class="info" target="_blank" href="http://www.linuxschools.com/karoshi/documentation/wiki/index.php?title=E-Mail_Access_Controls"><img class="images" alt="" src="/images/help/info.png"><span>'$"This allows you to set the level of access for sending and receiving E-Mails for your users."'<br><br>'$"Full access - allow the user to send and receive E-mails to all domains."'<br><br>'$"Restricted - limit the user to sending and receiving E-Mails from domains on the restricted list. This list defaults to your domain."'<br><br>'$"No Access - the user will not be able to send or receive any E-Mails."'</span></a></div><table class="tablesorter"><tbody><tr>'

	if [ "$ACTION" != viewrestrictionlist ]
	then
		echo '
		<td style="vertical-align: top; height: 30px; white-space: nowrap; min-width: '"$WIDTH"'px; text-align:center;">
			<form action="/cgi-bin/admin/email_access.cgi" method="post">
				<button class="info infonavbutton" name="_ViewList_" value="_ACTION_viewrestrictionlist_">
					<img src="'"$ICON1"'" alt="'$"View Restriction List"'">
					<span>'$"View the restriction list."'</span><br>
					'$"View Restriction List"'
				</button>
			</form>
		</td>

	'
	fi

	if [ "$ACTION" != getchoice ]
	then
		echo '
		<td style="vertical-align: top; height: 30px; white-space: nowrap; min-width: '"$WIDTH"'px; text-align:center;">
			<form action="/cgi-bin/admin/email_access.cgi" method="post">
				<button class="info" name="_ViewList_" value="_">
					<img src="'"$ICON2"'" alt="'$"Choose User / Group"'">
					<span>'$"Choose a user or group to change their E-Mail access."'</span><br>
					'$"Choose User / Group"'
				</button>
			</form>
		</td>

	'
	fi

	echo '</tr></table><br></div><div id="infobox">'
fi



Checksum=$(sha256sum /var/www/cgi-bin_karoshi/admin/email_access.cgi | cut -d' ' -f1)
echo "$REMOTE_USER:$REMOTE_ADDR:$Checksum:$ACTION:$USERSELECT:$ACCESSLEVEL:$GROUP:$MOBILE:email_access:" | sudo -H /opt/karoshi/web_controls/exec/email_access
[ "$MOBILE" = no ] && echo '</div>'
echo '</div></div></body></html>'
exit

